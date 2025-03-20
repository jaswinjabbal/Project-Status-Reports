package com.example.demo;

import java.sql.*;
import java.util.Properties;

public class MySQLConnection {
    public static void connectToMySQL() {
        int dynamicPort = 3307;  // Default port in case SSH fails


        //Pass port or term in here statically from the demo or api endpoint


        // 🔹 Get the forwarded SSH port dynamically
        if (ConnectToSSH.isSSHConnected()) {
            dynamicPort = ConnectToSSH.getForwardedPort(); // Get the actual SSH forwarded port
        } else {
            System.out.println(" SSH not connected. Using default port: " + dynamicPort);
        }

        // 🔹 JDBC URL WITHOUT database name
        String jdbcUrl = "jdbc:mysql://127.0.0.1:" + dynamicPort + "?useSSL=false&allowPublicKeyRetrieval=true&enabledTLSProtocols=TLSv1.2";
        
        //app
        //jdbc:mysql://127.0.0.1:${MYSQL_PORT}/${db.name}?useSSL=false&allowPublicKeyRetrieval=true&enabledTLSProtocols=TLSv1.2


        //
        System.out.println(" Connecting to MySQL with URL: " + jdbcUrl);

        // 🔹 Connection Properties
        Properties props = new Properties();
        props.setProperty("user", "ecen404team45");
        props.setProperty("password", "ecen404$592H#!cx");
        props.setProperty("useSSL", "false");
        props.setProperty("allowPublicKeyRetrieval", "true");
        props.setProperty("enabledTLSProtocols", "TLSv1.2");
        props.setProperty("connectTimeout", "5000");

        // 🔹 Establish Connection
        try (Connection connection = DriverManager.getConnection(jdbcUrl, props)) {
            System.out.println(" Connected to MySQL successfully!");

            // 🔹 Manually select the database
            try (Statement stmt = connection.createStatement()) {
                stmt.execute("USE `lusher engineering parts database`;");
                System.out.println(" Database selected successfully!");
            }

            // 🔹 Run Basic Tests
            runBasicTests(connection);

        } catch (SQLException e) {
            System.out.println(" MySQL Connection Failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void runBasicTests(Connection connection) {
        System.out.println("basic tests");

        // 🔹 Test 1: Check if the database contains any tables
        String checkTablesQuery = "SHOW TABLES;";
        try (Statement stmt = connection.createStatement(); ResultSet rs = stmt.executeQuery(checkTablesQuery)) {
            if (rs.next()) {
                System.out.println(" Test 1 Passed: Tables found in the database.");
            } else {
                System.out.println(" Test 1 Failed: No tables found in the database.");
            }
        } catch (SQLException e) {
            System.out.println(" Test 1 Failed: Unable to retrieve tables - " + e.getMessage());
        }

        // 🔹 Test 2: Check if a specific table (e.g., `parts`) exists
        String checkTableExistence = "SELECT 1 FROM `electronics_parts` LIMIT 1;";
        try (Statement stmt = connection.createStatement(); ResultSet rs = stmt.executeQuery(checkTableExistence)) {
            System.out.println(" Test 2 Passed: `parts` table exists and is accessible.");
        } catch (SQLException e) {
            System.out.println(" Test 2 Failed: `parts` table does not exist or is not accessible " + e.getMessage());
        }

        // 🔹 Test 3: Try fetching one row from `parts`
        String fetchDataQuery = "SELECT * FROM `electronics_parts` LIMIT 1;";
        try (Statement stmt = connection.createStatement(); ResultSet rs = stmt.executeQuery(fetchDataQuery)) {
            if (rs.next()) {
                System.out.println(" Test 3 Passed: Successfully retrieved a row from `parts`.");
            } else {
                System.out.println(" Test 3 Failed: `parts` table is empty.");
            }
        } catch (SQLException e) {
            System.out.println(" Test 3 Failed: Unable to fetch data from `parts` - " + e.getMessage());
        }

        System.out.println(" Database tests completed");
    }

    public static void main(String[] args) {
        connectToMySQL();
    }
}
