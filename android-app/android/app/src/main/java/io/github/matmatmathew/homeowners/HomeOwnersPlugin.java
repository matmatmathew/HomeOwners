package io.github.matmatmathew.homeowners;

import android.Manifest;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.provider.ContactsContract;
import android.provider.MediaStore;
import android.provider.Telephony;
import android.view.WindowManager;

import androidx.activity.result.ActivityResult;
import androidx.core.content.FileProvider;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Native features the HomeOwners web page can't get from the browser:
 * contact picker, reading text messages for a contact, sharing / saving files,
 * text shared into the app from other apps, and keeping the screen on.
 */
@CapacitorPlugin(
    name = "HomeOwners",
    permissions = { @Permission(alias = "sms", strings = { Manifest.permission.READ_SMS }) }
)
public class HomeOwnersPlugin extends Plugin {

    private String pendingShare = null;

    @Override
    public void load() {
        takeShare(getActivity().getIntent(), false);   // the app was opened from another app's Share menu
    }

    @Override
    protected void handleOnNewIntent(Intent intent) {
        super.handleOnNewIntent(intent);
        takeShare(intent, true);                       // shared while the app was already open
    }

    private void takeShare(Intent intent, boolean notify) {
        if (intent == null || !Intent.ACTION_SEND.equals(intent.getAction())) return;
        String text = intent.getStringExtra(Intent.EXTRA_TEXT);
        String subject = intent.getStringExtra(Intent.EXTRA_SUBJECT);
        String combined = (subject != null && !subject.isEmpty() && (text == null || !text.contains(subject)))
            ? subject + (text != null ? "\n" + text : "") : text;
        if (combined == null || combined.trim().isEmpty()) return;
        pendingShare = combined;
        intent.setAction(null);                        // don't hand the same share over twice
        if (notify) {
            JSObject data = new JSObject();
            data.put("text", combined);
            notifyListeners("sharedText", data, true);
        }
    }

    @PluginMethod
    public void getSharedText(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("text", pendingShare);
        pendingShare = null;
        call.resolve(ret);
    }

    // ---------- contacts: Android's own picker (no contacts permission needed)
    @PluginMethod
    public void pickContact(PluginCall call) {
        Intent intent = new Intent(Intent.ACTION_PICK, ContactsContract.CommonDataKinds.Phone.CONTENT_URI);
        startActivityForResult(call, intent, "contactPicked");
    }

    @ActivityCallback
    private void contactPicked(PluginCall call, ActivityResult result) {
        if (call == null) return;
        JSObject ret = new JSObject();
        if (result.getResultCode() != android.app.Activity.RESULT_OK || result.getData() == null || result.getData().getData() == null) {
            ret.put("cancelled", true);
            call.resolve(ret);
            return;
        }
        String[] cols = { ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER };
        try (Cursor c = getContext().getContentResolver().query(result.getData().getData(), cols, null, null, null)) {
            if (c != null && c.moveToFirst()) {
                ret.put("name", c.getString(0));
                ret.put("tel", c.getString(1));
            }
        } catch (Exception e) {
            call.reject("Could not read that contact: " + e.getMessage());
            return;
        }
        call.resolve(ret);
    }

    // ---------- text messages to and from one phone number
    @PluginMethod
    public void readSms(PluginCall call) {
        if (getPermissionState("sms") != PermissionState.GRANTED) {
            requestPermissionForAlias("sms", call, "smsPermission");
            return;
        }
        doReadSms(call);
    }

    @PermissionCallback
    private void smsPermission(PluginCall call) {
        if (getPermissionState("sms") == PermissionState.GRANTED) doReadSms(call);
        else call.reject("Permission to read text messages was not given.", "DENIED");
    }

    private static String lastDigits(String s, int n) {
        String d = s == null ? "" : s.replaceAll("[^0-9]", "");
        return d.length() > n ? d.substring(d.length() - n) : d;
    }

    private void doReadSms(PluginCall call) {
        String want = lastDigits(call.getString("phone", ""), 10);
        int limit = call.getInt("limit", 500);
        if (want.length() < 7) { call.reject("That contact has no usable phone number."); return; }
        String[] cols = { Telephony.Sms.ADDRESS, Telephony.Sms.DATE, Telephony.Sms.BODY, Telephony.Sms.TYPE };
        JSArray list = new JSArray();
        ContentResolver cr = getContext().getContentResolver();
        try (Cursor c = cr.query(Telephony.Sms.CONTENT_URI, cols, Telephony.Sms.ADDRESS + " LIKE ?",
                new String[] { "%" + want.substring(want.length() - 7) }, Telephony.Sms.DATE + " DESC")) {
            while (c != null && c.moveToNext() && list.length() < limit) {
                if (!lastDigits(c.getString(0), 10).equals(want)) continue;   // same last 7 digits isn't enough
                JSObject m = new JSObject();
                m.put("date", c.getLong(1));
                m.put("body", c.getString(2));
                m.put("sent", c.getInt(3) == Telephony.Sms.MESSAGE_TYPE_SENT);
                list.put(m);
            }
        } catch (Exception e) {
            call.reject("Could not read text messages: " + e.getMessage());
            return;
        }
        JSObject ret = new JSObject();
        ret.put("messages", list);
        call.resolve(ret);
    }

    // ---------- share a file to any app (Drive, OneDrive, Gmail…)
    @PluginMethod
    public void shareText(PluginCall call) {
        String name = call.getString("name", "homeowners-notes.txt");
        String text = call.getString("text", "");
        String mime = call.getString("mime", "text/plain");
        try {
            File dir = new File(getContext().getCacheDir(), "shared");
            if (!dir.exists()) dir.mkdirs();
            File[] old = dir.listFiles();
            if (old != null) for (File f : old) f.delete();
            File file = new File(dir, name.replaceAll("[\\\\/:*?\"<>|]", "_"));
            try (FileOutputStream out = new FileOutputStream(file)) { out.write(text.getBytes(StandardCharsets.UTF_8)); }
            Uri uri = FileProvider.getUriForFile(getContext(), getContext().getPackageName() + ".fileprovider", file);
            Intent send = new Intent(Intent.ACTION_SEND);
            send.setType(mime);
            send.putExtra(Intent.EXTRA_STREAM, uri);
            send.putExtra(Intent.EXTRA_SUBJECT, file.getName());
            send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            Intent chooser = Intent.createChooser(send, "Save HomeOwners backup to…");
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {   // don't offer HomeOwners itself as a place to send it
                chooser.putExtra(Intent.EXTRA_EXCLUDE_COMPONENTS, new android.content.ComponentName[] {
                    new android.content.ComponentName(getContext(), MainActivity.class) });
            }
            getActivity().startActivity(chooser);
            JSObject ret = new JSObject();
            ret.put("name", file.getName());
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Could not share the file: " + e.getMessage());
        }
    }

    // ---------- save a file into the phone's Downloads folder
    @PluginMethod
    public void saveDownload(PluginCall call) {
        String name = call.getString("name", "homeowners-notes.txt");
        String text = call.getString("text", "");
        String mime = call.getString("mime", "text/plain");
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) { shareText(call); return; }   // Android 9 and older: use the share menu
        try {
            ContentValues v = new ContentValues();
            v.put(MediaStore.Downloads.DISPLAY_NAME, name);
            v.put(MediaStore.Downloads.MIME_TYPE, mime);
            Uri uri = getContext().getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
            if (uri == null) throw new Exception("Downloads is not available");
            try (OutputStream out = getContext().getContentResolver().openOutputStream(uri)) { out.write(text.getBytes(StandardCharsets.UTF_8)); }
            JSObject ret = new JSObject();
            ret.put("where", "Downloads");
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Could not save to Downloads: " + e.getMessage());
        }
    }

    // ---------- keep the screen on while location tracking runs
    @PluginMethod
    public void keepAwake(PluginCall call) {
        boolean on = call.getBoolean("on", false);
        getActivity().runOnUiThread(() -> {
            if (on) getActivity().getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            else getActivity().getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            call.resolve();
        });
    }
}
