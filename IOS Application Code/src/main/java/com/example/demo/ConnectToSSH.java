package com.example.demo;

//e
//define imports
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.Session;
import java.util.Properties;

//public class callable by other classes under demo
public class ConnectToSSH {
    //Private class named ssHSession
    //Setting default port as 3307 in case dynamic port fails
    private static Session sshSession;
    private static int forwardedPort = 3307; 
    
    //Creation of connectToSSH Class callable by other functions
    public static void connectToSSH() {
        //try and catch block for error handling
        try {
            //Print Statement
            System.out.println(" Setting up SSH connection...");

            String sshUserEnv = System.getenv("sshUser");
            String sshPasswordEnv = System.getenv("sshPassword");

            // SSH Credentials. Note there is no database name here
            String sshHost = "lusherengineeringservices.com";
            int sshPort = 22;
            String sshUser = sshUserEnv;
            String sshPassword = sshPasswordEnv;

            System.out.println(" Connecting to SSH Host: " + sshHost);

            // Initialize JSch for SSH, this is part of the preinstalled package in order to inject the database credentials
            JSch jsch = new JSch();
            sshSession = jsch.getSession(sshUser, sshHost, sshPort);
            sshSession.setPassword(sshPassword);
            
            //
            Properties config = new Properties();
            config.put("StrictHostKeyChecking", "no");
            sshSession.setConfig(config);

            // Connect to SSH Server
            System.out.println(" Connecting to SSH Server...");
            sshSession.connect();

            // Forward local port dynamically assigned by the OS
            forwardedPort = sshSession.setPortForwardingL(0, "127.0.0.1", 3306); // Auto-assign available port
            System.out.println("  SSH Tunnel established" + forwardedPort);

             // Set MYSQL_PORT as a system property
            System.setProperty("MYSQL_PORT", String.valueOf(forwardedPort));

            //if something in the main function goes wrong this will catch the error
        } catch (Exception e) {
            System.err.println("  SSH Connection Failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    //After connection is complete the SSH Connection will be disabled as to not strain any server on Heroku
    public static void disconnectSSH() {
        if (sshSession != null && sshSession.isConnected()) {
            sshSession.disconnect();
            System.out.println("  SSH Tunnel Disconnected.");
        }
    }
    //Returns if the SSH is Connected or not for testing purposes
    public static boolean isSSHConnected() {
        return sshSession != null && sshSession.isConnected();
    }
    //gets the forwarded port for further MySQL Connections
    public static int getForwardedPort() {
        return forwardedPort;
    }
}
