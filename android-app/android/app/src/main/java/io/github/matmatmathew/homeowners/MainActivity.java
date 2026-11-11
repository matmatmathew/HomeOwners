package io.github.matmatmathew.homeowners;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(HomeOwnersPlugin.class);   // contacts, text messages, sharing, shared text, keep-awake
        super.onCreate(savedInstanceState);
    }
}
