package com.example.demo;

import java.sql.*;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class MySQLConnectionService {


    // Establish MySQL connection
    private Connection connectToDatabase() throws SQLException {
        // Ensure SSH is connected
        ConnectToSSH.connectToSSH();
        if (!ConnectToSSH.isSSHConnected()) {
            throw new SQLException("❌ SSH Connection failed. MySQL task could not be completed.");
        }

        return DriverManager.getConnection(
                "jdbc:mysql://127.0.0.1:" + System.getProperty("MYSQL_PORT") + "/lusher engineering parts database",
                "ecen404team45", "ecen404$592H#!cx");
    }

    // Search for a part by description
    public String getComplexQueryResults(String searchTerm) {
        String results = "";
        String query = "SELECT * FROM `electronics_parts` WHERE `Part Description` LIKE ? LIMIT";

        try (Connection connection = connectToDatabase();
             PreparedStatement stmt = connection.prepareStatement(query)) {

            stmt.setString(1, "%" + searchTerm + "%");
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                results += "Part Name: " + rs.getString("Part Description") + ", Part Description: " + rs.getString("Part Description") + "\n";
            }

        } catch (SQLException e) {
            e.printStackTrace();
            results = "❌ Error executing query: " + e.getMessage();
        } finally {
            ConnectToSSH.disconnectSSH();
        }

        return results.isEmpty() ? "No results found" : results;
    }

    // Delete a part by ID
    public String deletePart(int partId) {
        String query = "DELETE FROM `electronics_parts` WHERE `ID` = ?";

        try (Connection connection = connectToDatabase();
             PreparedStatement stmt = connection.prepareStatement(query)) {

            stmt.setInt(1, partId);
            int rowsAffected = stmt.executeUpdate();

            return (rowsAffected > 0) ? "✅ Part deleted successfully." : "❌ No part found with ID: " + partId;

        } catch (SQLException e) {
            e.printStackTrace();
            return "❌ Error deleting part: " + e.getMessage();
        } finally {
            ConnectToSSH.disconnectSSH();
        }
    }

    // Insert a new part
    public String insertPart(String partName, String partDescription) {
        String query = "INSERT INTO `electronics_parts` (`Part Name`, `Part Description`) VALUES (?, ?)";

        try (Connection connection = connectToDatabase();
             PreparedStatement stmt = connection.prepareStatement(query)) {

            stmt.setString(1, partName);
            stmt.setString(2, partDescription);
            int rowsInserted = stmt.executeUpdate();

            return (rowsInserted > 0) ? "✅ Part inserted successfully." : "❌ Failed to insert part.";

        } catch (SQLException e) {
            e.printStackTrace();
            return "❌ Error inserting part: " + e.getMessage();
        } finally {
            ConnectToSSH.disconnectSSH();
        }
    }

    // Update a part description by ID
    public ResponseEntity<?> updatePart(Map<String, String> partData) {
        // Validate and parse ID from JSON
        String idStr = partData.get("id");
        if (idStr == null || idStr.isEmpty()) {
            return ResponseEntity.badRequest().body("❌ ID is required to update a part.");
        }
    
        int id;
        try {
            id = Integer.parseInt(idStr);
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest().body("❌ Invalid ID format.");
        }
    
        // Retrieve and parse required fields
        String partDescription = partData.get("partDescription");
        String manufacturer = partData.get("manufacturer");
        String supplier1 = partData.get("supplier1");
        String supplierPartNumber = partData.get("supplierPartNumber");
        int rohsCompliant = Integer.parseInt(partData.getOrDefault("rohsCompliant", "0"));
        int partVerified = Integer.parseInt(partData.getOrDefault("partVerified", "0"));
        int autoUpdate = Integer.parseInt(partData.getOrDefault("autoUpdate", "0"));
    
        // Get an existing MySQL connection
        try (Connection connection = connectToDatabase()) {
    
            // Construct SQL update query
            String updateQuery = "UPDATE `electronics_parts` SET " +
                    "`Part Description` = ?, " +
                    "`Manufacturer` = ?, " +
                    "`Supplier 1` = ?, " +
                    "`Supplier Part Number 1` = ?, " +
                    "`RoHS Compliant` = ?, " +
                    "`Part Verified` = ?, " +
                    "`Auto Update` = ? " +
                    "WHERE `ID` = ?";
    
            try (PreparedStatement stmt = connection.prepareStatement(updateQuery)) {
                int index = 1;
                stmt.setString(index++, partDescription);
                stmt.setString(index++, manufacturer);
                stmt.setString(index++, supplier1);
                stmt.setString(index++, supplierPartNumber);
                stmt.setInt(index++, rohsCompliant);
                stmt.setInt(index++, partVerified);
                stmt.setInt(index++, autoUpdate);
                stmt.setInt(index, id); // Set ID as the last parameter
    
                int rowsUpdated = stmt.executeUpdate();
                if (rowsUpdated > 0) {
                    return ResponseEntity.ok("✅ Part with ID " + id + " updated successfully.");
                } else {
                    return ResponseEntity.status(HttpStatus.NOT_FOUND).body("⚠️ Part with ID " + id + " not found.");
                }
            }
    
        } catch (SQLException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("❌ Error updating part: " + e.getMessage());
        }
    }
    


    //admin check
    
    private static final Set<String> ADMIN_EMAILS = new HashSet<>(Set.of(
        "raindude10@gmail.com",
        "admin2@example.com",
        "superuser@example.com"
    ));
    public boolean isAdmin(String email) {
        return ADMIN_EMAILS.contains(email.toLowerCase());
    }

    public boolean addAdmin(String email) {
        return ADMIN_EMAILS.add(email.toLowerCase()); // Returns true if added, false if already exists
    }
}
