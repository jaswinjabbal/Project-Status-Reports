package com.example.demo;

//import java maps which is important to map out JSON Return values for further flutterflow parsing
import java.util.HashMap;
import java.util.Map;
import java.util.List;

//import spring-boot frameworks
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;



import org.springframework.http.MediaType;

//rest controller which handles all the API points for this controller
//the main function of this controller is to handle the input and output logic while leaving the filter logic to the MySQL Service class

@RestController
public class MySQLController {

    @Autowired
    private MySQLConnectionService mySQLConnectionService;

    // Search for parts
    @GetMapping("/query")
    public ResponseEntity<String> getComplexQueryResults(@RequestParam String searchTerm) {
        String jsonResponse = mySQLConnectionService.getComplexQueryResults(searchTerm);
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(jsonResponse);
    }

    //add a part
    @PostMapping("/insert-part")
    public ResponseEntity<?> insertPart(@RequestBody Map<String, String> partData) {
        return mySQLConnectionService.insertPart(partData);
    }

    // Delete a part
    @DeleteMapping("/delete-part")
    public String deletePart(@RequestParam int id) {
        String result = mySQLConnectionService.deletePart(id);
        return " Delete operation completed " + result;
    }

    // Update a part's description
    @PostMapping("/updatePart")
    public ResponseEntity<?> updatePart(@RequestBody Map<String, String> partData) {
        return mySQLConnectionService.updatePart(partData);
    }


    //admin check
    @GetMapping("/check-admin")
    public ResponseEntity<Map<String, Boolean>> checkAdmin(@RequestParam String email) {
        Map<String, Boolean> response = new HashMap<>();
        response.put("isAdmin", mySQLConnectionService.isAdmin(email));
        return ResponseEntity.ok(response);
    }

    // Add a new admin email
    @PostMapping("/add-admin")
    public String addAdmin(@RequestParam String email) {
        boolean added = mySQLConnectionService.addAdmin(email);
        return added ? " Email added as admin " + email : " Email is already an admin.";
    }

    //static list of permissions inside the app, this is specifically for the home page, which can be updated through settings->Admin Settings->Configure the four switches
    private static final Map<String, Boolean> USER_PERMISSIONS = new HashMap<>(Map.of(
        "allowDelete", false,
        "allowAdd", false,
        "allowUpdate", false,
        "allowTag", false
    ));

    // API to get current user permissions
    @GetMapping("/get")
    public ResponseEntity<Map<String, Boolean>> getUserPermissions() {
        return ResponseEntity.ok(USER_PERMISSIONS);
    }

    // API to update user permissions
    @PostMapping("/update")
    public ResponseEntity<String> updateUserPermissions(@RequestBody Map<String, Boolean> newPermissions) {
        USER_PERMISSIONS.putAll(newPermissions);
        return ResponseEntity.ok("User permissions updated successfully.");
    }
    
    //Getting Column Names
    @GetMapping("/get-column-names")
    public ResponseEntity<String> getColumnNames() {
        String columnJson = mySQLConnectionService.getColumnNames();
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(columnJson);
    }


    //column name from flutterflow
    @GetMapping("/get-values-by-column")
    public ResponseEntity<String> getValuesByColumn(@RequestParam String columnName) {
        String jsonResponse = mySQLConnectionService.getValuesByColumn(columnName);
    return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(jsonResponse);
}


    //------------search filter
// ------------ Search + Filter API Endpoint
@GetMapping("/filter-parts-by-column")
public ResponseEntity<String> filterPartsByColumn(
        @RequestParam(required = false) String columnName,
        @RequestParam(required = false) String value,
        @RequestParam(required = false) String searchTerm) {

    // Call your service function with the new searchTerm parameter
    String response = mySQLConnectionService.getFilteredComplexResults(columnName, value, searchTerm);
    return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body(response);
}



//------color


}
