package com.example.demo;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;

//http://localhost:8080/perform-mysql-task?searchTerm=cap
//Invoke-WebRequest -Uri "http://localhost:8080/insert-part?partName=Resistor&partDescription=10KΩ" -Method POST | Select-Object -ExpandProperty Content
//Invoke-WebRequest -Uri "http://localhost:8080/delete-part?id=123" -Method DELETE | Select-Object -ExpandProperty Content
//Invoke-WebRequest -Uri "http://localhost:8080/update-part?id=123&newDescription=UpdatedValue" -Method PUT | Select-Object -ExpandProperty Content


//update heroku https://startapp2-0bb4c947841d.herokuapp.com/updatePart


//admin check
//https://your-app.herokuapp.com/check-admin?email=user@example.com
//https://startapp2-0bb4c947841d.herokuapp.com/check-admin?email=your_email@example.com


@RestController
public class MySQLController {

    // Example URLs:
    // Search: https://your-app.herokuapp.com/perform-mysql-task?searchTerm=capacitor
    // Insert: https://your-app.herokuapp.com/insert-part?partName=Resistor&partDescription=10KΩ
    // Delete: https://your-app.herokuapp.com/delete-part?id=123
    // Update: https://your-app.herokuapp.com/update-part?id=123&newDescription=UpdatedValue

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
    

}
