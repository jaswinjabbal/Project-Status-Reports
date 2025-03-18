package com.example.demo;

import com.jcraft.jsch.JSch;
import com.jcraft.jsch.Session;
import java.util.Properties;

public class ConnectToSSH {
    private static Session sshSession;
    private static int forwardedPort = 3307; 
    public static void connectToSSH() {
        try {
            System.out.println(" Setting up SSH connection...");

            // SSH Credentials
            String sshHost = "lusherengineeringservices.com";
            int sshPort = 22;
            String sshUser = "ecen404team45";
            String sshPassword = "ecen404$592H#!cx";

            System.out.println("🔍 Connecting to SSH Host: " + sshHost);

            // Initialize JSch for SSH
            JSch jsch = new JSch();
            sshSession = jsch.getSession(sshUser, sshHost, sshPort);
            sshSession.setPassword(sshPassword);

            Properties config = new Properties();
            config.put("StrictHostKeyChecking", "no");
            sshSession.setConfig(config);

            // Connect to SSH Server
            System.out.println(" Connecting to SSH Server...");
            sshSession.connect();

            // 🔹 Forward local port dynamically assigned by the OS
            forwardedPort = sshSession.setPortForwardingL(0, "127.0.0.1", 3306); // Auto-assign available port
            System.out.println(" ✅ SSH Tunnel established! MySQL accessible via local port: " + forwardedPort);

             // Set MYSQL_PORT as a system property
            System.setProperty("MYSQL_PORT", String.valueOf(forwardedPort));


        } catch (Exception e) {
            System.err.println(" ❌ SSH Connection Failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void disconnectSSH() {
        if (sshSession != null && sshSession.isConnected()) {
            sshSession.disconnect();
            System.out.println(" 🔌 SSH Tunnel Disconnected.");
        }
    }

    public static boolean isSSHConnected() {
        return sshSession != null && sshSession.isConnected();
    }

    public static int getForwardedPort() {
        return forwardedPort;
    }
}
