package com.example.demo;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
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
    @GetMapping("/perform-mysql-task")
    public String performMySQLTask(@RequestParam String searchTerm) {
        String results = mySQLConnectionService.getComplexQueryResults(searchTerm);
        return "✅ MySQL task completed successfully! Results: " + results;
    }

    // Insert a new part
    @PostMapping("/insert-part")
    public String insertPart(@RequestParam String partName, @RequestParam String partDescription) {
        String result = mySQLConnectionService.insertPart(partName, partDescription);
        return "✅ Insert operation completed! " + result;
    }

    // Delete a part
    @DeleteMapping("/delete-part")
    public String deletePart(@RequestParam int id) {
        String result = mySQLConnectionService.deletePart(id);
        return "✅ Delete operation completed! " + result;
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
        return added ? "✅ Email added as admin: " + email : "⚠️ Email is already an admin.";
    }
    

}
