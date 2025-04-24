package com.example.demo;

import java.sql.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONObject;


import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

//service class which mimicks the MySqlConnection class but makes it callable and enables value return
@Service
public class MySQLConnectionService {


    // Establish MySQL connection
    private Connection connectToDatabase() throws SQLException {
        // Ensure SSH is connected
        ConnectToSSH.connectToSSH();
        if (!ConnectToSSH.isSSHConnected()) {
            throw new SQLException(" SSH Connection failed. MySQL task could not be completed.");
        }
        
        //gets the dynamic port from the SSH Connection
        return DriverManager.getConnection(
                "jdbc:mysql://127.0.0.1:" + System.getProperty("MYSQL_PORT") + "/lusher engineering parts database", System.getenv("sshUser"), System.getenv("sshPassword"));
    }



//------------------------------------------------------------------------------------------------------------------------------------------------SEARCH

// Search for a part by description
public String getComplexQueryResults(Object input) {
    JSONArray jsonArray = new JSONArray();
    
    // Convert any input to a safe string
    String searchTerm = (input == null) ? "" : input.toString().trim();

    // Handle completely empty or invalid input early
    if (searchTerm.isEmpty()) {
        return "{ \"success\": false, \"error\": \"Empty search term provided\" }";
    }

    String query = "SELECT `ID`, `Part Description`, `Manufacturer`, `Manufacturer Part Number`, `Supplier 1`, `Supplier Part Number 1`, `Part Category`, `Cost 1pc`, `Cost 100pc`, `Cost 1000pc`, `Notes`, `Project List` " +
                   "FROM `electronics_parts` WHERE `Part Description` LIKE ? LIMIT 10";

    try (Connection connection = connectToDatabase();
         PreparedStatement stmt = connection.prepareStatement(query)) {

        stmt.setString(1, "%" + searchTerm + "%");
        ResultSet rs = stmt.executeQuery();

        while (rs.next()) {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", rs.getInt("ID"));
            jsonObject.put("partDescription", rs.getString("Part Description"));
            jsonObject.put("manufacturer", rs.getString("Manufacturer"));
            jsonObject.put("manufacturerPartNumber", rs.getString("Manufacturer Part Number"));
            jsonObject.put("supplier1", rs.getString("Supplier 1"));
            jsonObject.put("supplierPartNumber1", rs.getString("Supplier Part Number 1"));
            jsonObject.put("partCategory", rs.getString("Part Category"));

            // Use safe parser to handle non-numeric values
            jsonObject.put("cost1pc", parseDoubleSafe(rs.getString("Cost 1pc")));
            jsonObject.put("cost100pc", parseDoubleSafe(rs.getString("Cost 100pc")));
            jsonObject.put("cost1000pc", parseDoubleSafe(rs.getString("Cost 1000pc")));

            jsonObject.put("notes", rs.getString("Notes"));
            jsonObject.put("projectList", rs.getString("Project List"));
            jsonArray.put(jsonObject);
        }

        if (jsonArray.isEmpty()) {
            return "{ \"success\": false, \"error\": \"No results found\" }";
        } else {
            return jsonArray.toString();
        }

    } catch (SQLException e) {
        e.printStackTrace();
        return "{ \"success\": false, \"error\": \"" + e.getMessage() + "\" }";
    } finally {
        ConnectToSSH.disconnectSSH();
    }
}

// Helper method to safely parse numeric strings
private Object parseDoubleSafe(String value) {
    try {
        return Double.parseDouble(value);
    } catch (Exception e) {
        return "N/A"; // Or return 0.0 if you'd prefer numeric fallback
    }
}




//-----------------------------------------------------------------------------------------------------------------------------------------------DELETE
    // Delete a part by ID
    public String deletePart(int partId) {
        //delete function based on mysql ID
        String query = "DELETE FROM `electronics_parts` WHERE `ID` = ?";

        //tries the connection and inserts the delete query
        try (Connection connection = connectToDatabase();
             PreparedStatement stmt = connection.prepareStatement(query)) {
            
            stmt.setInt(1, partId);
            int rowsAffected = stmt.executeUpdate();

            return (rowsAffected > 0) ? " Part deleted successfully." : " No part found with ID: " + partId;
        
        //catches any errors
        } catch (SQLException e) {
            e.printStackTrace();
            return " Error deleting part: " + e.getMessage();
        } finally {
            ConnectToSSH.disconnectSSH();
        }
    }

//-----------------------------------------------------------------------------------------------------------------------ADD
// add a new part


public ResponseEntity<?> insertPart(Map<String, String> partData) {
    // Extract and validate required fields
    try {
        String partDescription = partData.getOrDefault("partDescription", "").trim();
        String manufacturer = partData.getOrDefault("manufacturer", "").trim();
        String manufacturerPN = partData.getOrDefault("manufacturerPN", "").trim();
        String supplier1 = partData.getOrDefault("supplier1", "").trim();
        String supplierPartNumber = partData.getOrDefault("supplierPartNumber", "").trim();
        String partCategory = partData.getOrDefault("partCategory", "").trim();
        String cost1pc = partData.getOrDefault("cost1pc", null);
        String cost100pc = partData.getOrDefault("cost100pc", null);
        String cost1000pc = partData.getOrDefault("cost1000pc", null);
        String tags = partData.getOrDefault("Tags", null);
        String verifiedBy = partData.getOrDefault("VerifiedBy", null);
        String projectList = partData.getOrDefault("ProjectList", null);
        String libraryRef = partData.getOrDefault("LibraryRef", null);
        String libraryPath = partData.getOrDefault("LibraryPath", null);
        String footprint = partData.getOrDefault("Footprint", null);
        String footprintRef = partData.getOrDefault("FootprintRef", null);
        String footprintPath = partData.getOrDefault("FootprintPath", null);

    System.out.println("Received partData map: " + partData);
    System.out.println("FootprintPath raw value: " + partData.get("FootprintPath"));
    System.out.println("FootprintPath class type: " +
    (partData.get("FootprintPath") != null ? partData.get("FootprintPath").getClass() : "null"));


        int rohsCompliant = parseIntOrDefault(partData.get("rohsCompliant"), 0);
        int partVerified = parseIntOrDefault(partData.get("partVerified"), 0);
        int autoUpdate = parseIntOrDefault(partData.get("autoUpdate"), 0);
        int internalPN = parseIntOrDefault(partData.get("InternalPN"), 0);

        // Validate required fields
        if (partDescription.isEmpty() || manufacturer.isEmpty() || supplier1.isEmpty() || supplierPartNumber.isEmpty() || manufacturerPN.isEmpty()) {
            return ResponseEntity.badRequest().body("Missing required fields, Manufacturer & PN, Supplier & PN");
        }

        // Open database connection
        try (Connection connection = connectToDatabase()) {

            // Get the last ID and increment by 1
            int newID = 1;
            String idQuery = "SELECT MAX(ID) FROM electronics_parts";
            try (PreparedStatement idStmt = connection.prepareStatement(idQuery);
                 ResultSet rs = idStmt.executeQuery()) {
                if (rs.next() && rs.getInt(1) > 0) {
                    newID = rs.getInt(1) + 1;
                }
            }

            // Updated SQL Insert Statement including all new fields
            String insertQuery = "INSERT INTO electronics_parts " +
                    "(`ID`, `Internal PN`, `Part Description`, `Manufacturer`, `Manufacturer Part Number`, `Supplier 1`, " +
                    "`Supplier Part Number 1`, `Part Category`, `RoHS Compliant`, `Part Verified`, `Auto Update`, " +
                    "`Cost 1pc`, `Cost 100pc`, `Cost 1000pc`, `Tags`, `Verified By`, `Project List`, " +
                    "`Library Ref`, `Library Path`, `Footprint`, `Footprint Ref`, `Footprint Path`) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

            try (PreparedStatement stmt = connection.prepareStatement(insertQuery)) {
                int index = 1;
                stmt.setInt(index++, newID);
                stmt.setInt(index++, internalPN);
                stmt.setString(index++, partDescription);
                stmt.setString(index++, manufacturer);
                stmt.setString(index++, manufacturerPN);
                stmt.setString(index++, supplier1);
                stmt.setString(index++, supplierPartNumber);
                stmt.setString(index++, partCategory);
                stmt.setInt(index++, rohsCompliant);
                stmt.setInt(index++, partVerified);
                stmt.setInt(index++, autoUpdate);
                stmt.setString(index++, cost1pc);
                stmt.setString(index++, cost100pc);
                stmt.setString(index++, cost1000pc);
                stmt.setString(index++, tags);
                stmt.setString(index++, verifiedBy);
                stmt.setString(index++, projectList);
                stmt.setString(index++, libraryRef);
                stmt.setString(index++, libraryPath);
                stmt.setString(index++, footprint);
                stmt.setString(index++, footprintRef);
                stmt.setString(index++, footprintPath);

                int rowsInserted = stmt.executeUpdate();

                if (rowsInserted > 0) {
                    return ResponseEntity.ok("Part inserted successfully with ID: " + newID);
                } else {
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to insert part.");
                }
            }
        }
    } catch (SQLException e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Error inserting part: " + e.getMessage());
    }
}

// Helper method to safely parse integers
private int parseIntOrDefault(String value, int defaultValue) {
    try {
        return (value != null && !value.isEmpty()) ? Integer.parseInt(value) : defaultValue;
    } catch (NumberFormatException e) {
        return defaultValue;
    }
}

    
    
    
    
    
    //----------------------------------------------------------------------------------------------------------------------------UPDATE
    // Update a part description by ID


    public ResponseEntity<?> updatePart(Map<String, String> partData) {

        // Validate and parse ID from JSON
        String idStr = partData.get("id");
        if (idStr == null || idStr.isEmpty()) {
            return ResponseEntity.badRequest().body("ID is required to update a part.");
        }
    
        int id;
        try {
            id = Integer.parseInt(idStr);
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest().body("Invalid ID format.");
        }
    
        // Retrieve and parse all required fields
        int internalPN = parseIntOrDefault(partData.get("InternalPN"), 0);
        String partDescription = partData.get("partDescription");
        String manufacturer = partData.get("manufacturer");
        String manufacturerPN = partData.get("manufacturerPN");
        String supplier1 = partData.get("supplier1");
        String supplierPartNumber = partData.get("supplierPartNumber");
        String partCategory = partData.get("partCategory");
        int rohsCompliant = parseIntOrDefault(partData.get("rohsCompliant"), 0);
        int partVerified = parseIntOrDefault(partData.get("partVerified"), 0);
        int autoUpdate = parseIntOrDefault(partData.get("autoUpdate"), 0);
        String cost1pc = partData.getOrDefault("cost1pc", null);
        String cost100pc = partData.getOrDefault("cost100pc", null);
        String cost1000pc = partData.getOrDefault("cost1000pc", null);
        String tags = partData.getOrDefault("Tags", null);
        String verifiedBy = partData.getOrDefault("VerifiedBy", null);
        String projectList = partData.getOrDefault("ProjectList", null);
        String libraryRef = partData.getOrDefault("LibraryRef", null);
        String libraryPath = partData.getOrDefault("LibraryPath", null);
        String footprint = partData.getOrDefault("Footprint", null);
        String footprintRef = partData.getOrDefault("FootprintRef", null);
        String footprintPath = partData.getOrDefault("FootprintPath", null);
    
        try (Connection connection = connectToDatabase()) {
    
            String updateQuery = "UPDATE `electronics_parts` SET " +
                    "`Internal PN` = ?, " +
                    "`Part Description` = ?, " +
                    "`Manufacturer` = ?, " +
                    "`Manufacturer Part Number` = ?, " +
                    "`Supplier 1` = ?, " +
                    "`Supplier Part Number 1` = ?, " +
                    "`Part Category` = ?, " +
                    "`RoHS Compliant` = ?, " +
                    "`Part Verified` = ?, " +
                    "`Auto Update` = ?, " +
                    "`Cost 1pc` = ?, " +
                    "`Cost 100pc` = ?, " +
                    "`Cost 1000pc` = ?, " +
                    "`Tags` = ?, " +
                    "`Verified By` = ?, " +
                    "`Project List` = ?, " +
                    "`Library Ref` = ?, " +
                    "`Library Path` = ?, " +
                    "`Footprint` = ?, " +
                    "`Footprint Ref` = ?, " +
                    "`Footprint Path` = ? " +
                    "WHERE `ID` = ?";
    
            try (PreparedStatement stmt = connection.prepareStatement(updateQuery)) {
                int index = 1;
                stmt.setInt(index++, internalPN);
                stmt.setString(index++, partDescription);
                stmt.setString(index++, manufacturer);
                stmt.setString(index++, manufacturerPN);
                stmt.setString(index++, supplier1);
                stmt.setString(index++, supplierPartNumber);
                stmt.setString(index++, partCategory);
                stmt.setInt(index++, rohsCompliant);
                stmt.setInt(index++, partVerified);
                stmt.setInt(index++, autoUpdate);
                stmt.setString(index++, cost1pc);
                stmt.setString(index++, cost100pc);
                stmt.setString(index++, cost1000pc);
                stmt.setString(index++, tags);
                stmt.setString(index++, verifiedBy);
                stmt.setString(index++, projectList);
                stmt.setString(index++, libraryRef);
                stmt.setString(index++, libraryPath);
                stmt.setString(index++, footprint);
                stmt.setString(index++, footprintRef);
                stmt.setString(index++, footprintPath);
                stmt.setInt(index, id); // Last parameter is ID
    
                int rowsUpdated = stmt.executeUpdate();
                if (rowsUpdated > 0) {
                    return ResponseEntity.ok("Part with ID " + id + " updated successfully.");
                } else {
                    return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Part with ID " + id + " not found.");
                }
            }
    
        } catch (SQLException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error updating part: " + e.getMessage());
        }
    }
    

    //admin check
    //------------------------------------------------------------------------------------------------------------------------------------------ADMIN
    private static final Set<String> ADMIN_EMAILS = new HashSet<>(Set.of(
        "raindude10@gmail.com",
        "admin2@example.com",
        "superuser@example.com",
        "john.lusher@tamu.edu",
        "tony.beneventi@tamu.edu"
        //list of admin emails
    ));
    public boolean isAdmin(String email) {
        return ADMIN_EMAILS.contains(email.toLowerCase());
    }

    public boolean addAdmin(String email) {
        return ADMIN_EMAILS.add(email.toLowerCase()); // Returns true if added, false if already exists
    }

//---------------------------------------------------------------------------------------------------------------------------------------------

// Get all column names from the electronics_parts table
public String getColumnNames() {
    String query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'electronics_parts'";
    StringBuilder jsonBuilder = new StringBuilder();
    jsonBuilder.append("{");

    try (Connection connection = connectToDatabase();
         PreparedStatement stmt = connection.prepareStatement(query);
         ResultSet rs = stmt.executeQuery()) {

        int index = 1;
        while (rs.next()) {
            String columnName = rs.getString("COLUMN_NAME");
            jsonBuilder.append("\"columnName").append(index).append("\":\"")
                       .append(columnName).append("\",");
            index++;
        }

        // Remove the trailing comma and close the JSON object
        if (jsonBuilder.charAt(jsonBuilder.length() - 1) == ',') {
            jsonBuilder.setLength(jsonBuilder.length() - 1);
        }
        jsonBuilder.append("}");

        return jsonBuilder.toString();

    } catch (SQLException e) {
        e.printStackTrace();
        return "{\"error\":\"Failed to fetch column names: " + e.getMessage() + "\"}";
    } finally {
        ConnectToSSH.disconnectSSH();
    }

}
    //--------------------------------------------------------------------------------------
    //getting information from under the column
    

// Get distinct values under a specific column from electronics_parts
public String getValuesByColumn(String columnName) {
    // Basic SQL with column name injected (sanitize carefully!)
    String query = "SELECT DISTINCT `" + columnName + "` FROM electronics_parts";

    StringBuilder jsonBuilder = new StringBuilder();
    jsonBuilder.append("{");

    try (Connection connection = connectToDatabase();
         PreparedStatement stmt = connection.prepareStatement(query);
         ResultSet rs = stmt.executeQuery()) {

        int index = 1;
        while (rs.next()) {
            String value = rs.getString(columnName);
            if (value == null || value.trim().isEmpty()) continue;
            jsonBuilder.append("\"value").append(index).append("\":\"")
                       .append(value.replace("\"", "\\\"")).append("\",");
            index++;
        }

        if (jsonBuilder.charAt(jsonBuilder.length() - 1) == ',') {
            jsonBuilder.setLength(jsonBuilder.length() - 1);
        }
        jsonBuilder.append("}");

        return jsonBuilder.toString();

    } catch (SQLException e) {
        e.printStackTrace();
        return "{\"error\":\"Failed to fetch values: " + e.getMessage() + "\"}";
    } finally {
        ConnectToSSH.disconnectSSH();
    }



    
}
//------------------------------------------------------------------------------------------------------
//search two





public String getFilteredComplexResults(String columnName, String value, String searchTerm) {
    JSONArray jsonArray = new JSONArray();
    String query;

    boolean noFilter = columnName == null || columnName.trim().isEmpty();
    boolean filterByValue = value != null && !value.trim().isEmpty();
    boolean hasSearchTerm = searchTerm != null && !searchTerm.trim().isEmpty();

    if (!noFilter) {
        columnName = columnName.trim();
        List<String> allowedColumns = List.of(
            "Manufacturer",
            "Part Description",
            "Manufacturer Part Number",
            "Supplier 1",
            "Supplier Part Number 1",
            "Part Category",
            "Project List"
        );

        if (!allowedColumns.contains(columnName)) {
            return "{ \"success\": false, \"error\": \"Unsupported column name.\" }";
        }
    }

    //error handling
    if (!noFilter && !filterByValue && !hasSearchTerm) {
        return "{ \"success\": false, \"error\": \"No Column Value\" }";
    }

    String selectFields = "`ID`, `Part Description`, `Manufacturer`, `Manufacturer Part Number`, `Supplier 1`, " +
            "`Supplier Part Number 1`, `Part Category`, `Cost 1pc`, `Cost 100pc`, `Cost 1000pc`, `Notes`, " +
            "`Project List`, `Primary Vendor Stock`, `Library Ref`, `Library Path`, `Footprint`, `Footprint Ref`, " +
            "`Footprint Path`, `Tags`, `RoHS Compliant`, `Updated`, `Current Inventory`, `Verified By`";

    if (noFilter && !hasSearchTerm) {
        query = "SELECT " + selectFields + " FROM `electronics_parts` LIMIT 50";
    } else if (noFilter && hasSearchTerm) {
        query = "SELECT " + selectFields + " FROM `electronics_parts` WHERE LOWER(`Part Description`) LIKE ? LIMIT 50";
    } else if (filterByValue && !hasSearchTerm) {
        query = "SELECT " + selectFields + " FROM `electronics_parts` WHERE LOWER(`" + columnName + "`) LIKE ? LIMIT 50";
    } else {
        query = "SELECT " + selectFields + " FROM `electronics_parts` WHERE LOWER(`" + columnName + "`) LIKE ? AND LOWER(`Part Description`) LIKE ? LIMIT 50";
    }

    try (Connection connection = connectToDatabase();
         PreparedStatement stmt = connection.prepareStatement(query)) {

        if (!noFilter && filterByValue && hasSearchTerm) {
            stmt.setString(1, "%" + value.toLowerCase() + "%");
            stmt.setString(2, "%" + searchTerm.toLowerCase() + "%");
        } else if (!noFilter && filterByValue) {
            stmt.setString(1, "%" + value.toLowerCase() + "%");
        } else if (noFilter && hasSearchTerm) {
            stmt.setString(1, "%" + searchTerm.toLowerCase() + "%");
        }

        ResultSet rs = stmt.executeQuery();
        int index = 0;

        while (rs.next()) {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", rs.getInt("ID"));
            jsonObject.put("partDescription", rs.getString("Part Description"));
            jsonObject.put("manufacturer", rs.getString("Manufacturer"));
            jsonObject.put("manufacturerPartNumber", rs.getString("Manufacturer Part Number"));
            jsonObject.put("supplier1", rs.getString("Supplier 1"));
            jsonObject.put("supplierPartNumber1", rs.getString("Supplier Part Number 1"));
            jsonObject.put("partCategory", rs.getString("Part Category"));
            jsonObject.put("cost1pc", safeDouble(rs.getString("Cost 1pc")));
            jsonObject.put("cost100pc", safeDouble(rs.getString("Cost 100pc")));
            jsonObject.put("cost1000pc", safeDouble(rs.getString("Cost 1000pc")));
            jsonObject.put("notes", rs.getString("Notes") != null ? rs.getString("Notes") : "");
            jsonObject.put("projectList", rs.getString("Project List") != null ? rs.getString("Project List") : "");

            jsonObject.put("primaryVendorStock", rs.getInt("Primary Vendor Stock"));
            jsonObject.put("libraryRef", rs.getString("Library Ref"));
            jsonObject.put("libraryPath", rs.getString("Library Path"));
            jsonObject.put("footprint", rs.getString("Footprint"));
            jsonObject.put("footprintRef", rs.getString("Footprint Ref"));
            jsonObject.put("footprintPath", rs.getString("Footprint Path"));
            jsonObject.put("tags", rs.getString("Tags"));
            jsonObject.put("rohsCompliant", rs.getInt("RoHS Compliant"));
            jsonObject.put("updated", rs.getString("Updated"));
            jsonObject.put("currentInventory", rs.getInt("Current Inventory"));
            jsonObject.put("verifiedBy", rs.getString("Verified By"));

            String rowColor = (index % 2 == 0) ? "#000000" : "#FFFFFF";
            jsonObject.put("rowColor", rowColor);

            jsonArray.put(jsonObject);
            index++;
        }

        //  Handle no results (add BOTH "NO RESULTS FOUND" and "END OF LIST"):
        if (jsonArray.length() == 0) {
            jsonArray.put(buildPlaceholderRow("NO RESULTS FOUND"));
            jsonArray.put(buildPlaceholderRow("END OF LIST"));
        } else {
            jsonArray.put(buildPlaceholderRow("END OF LIST"));
        }

        JSONObject finalResponse = new JSONObject();
        finalResponse.put("results", jsonArray);
        return finalResponse.toString();

    } catch (SQLException e) {
        e.printStackTrace();
        return "{ \"success\": false, \"error\": \"" + e.getMessage() + "\" }";
    } finally {
        ConnectToSSH.disconnectSSH();
    }
}

private JSONObject buildPlaceholderRow(String message) {
    JSONObject placeholder = new JSONObject();
    placeholder.put("id", -1);
    placeholder.put("partDescription", message);
    placeholder.put("manufacturer", "");
    placeholder.put("manufacturerPartNumber", "");
    placeholder.put("supplier1", "");
    placeholder.put("supplierPartNumber1", "");
    placeholder.put("partCategory", "");
    placeholder.put("cost1pc", 0.0);
    placeholder.put("cost100pc", 0.0);
    placeholder.put("cost1000pc", 0.0);
    placeholder.put("notes", "");
    placeholder.put("projectList", "");
    placeholder.put("primaryVendorStock", 0);
    placeholder.put("libraryRef", "");
    placeholder.put("libraryPath", "");
    placeholder.put("footprint", "");
    placeholder.put("footprintRef", "");
    placeholder.put("footprintPath", "");
    placeholder.put("tags", "");
    placeholder.put("rohsCompliant", 0);
    placeholder.put("updated", "");
    placeholder.put("currentInventory", 0);
    placeholder.put("verifiedBy", "");
    placeholder.put("rowColor", "#FFFFFF");
    return placeholder;
}

private double safeDouble(String s) {
    try {
        if (s == null || s.trim().isEmpty() || s.equalsIgnoreCase("N/A")) return 0.0;
        return Double.parseDouble(s.trim());
    } catch (NumberFormatException e) {
        return 0.0;
    }
}




//----------------------------------------------------------


}