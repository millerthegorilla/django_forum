Feature: Profile page
    
    Scenario: Visiting the profile page
        Given User is logged in
        When User visits the profile page
        Then User can see the display_name input
        And User can see the username input
        And User can see the email input
        And User can see the first_name input
        And User can see the last_name input
        And Address details are hidden


    Scenario: Cannot see the profile page
        Given User is not logged in
        When User visits the profile page
        Then User is redirected to login page


    Scenario: Updating profile fields
        Given User is logged in
        When User visits the profile page
        And User enters different information
        And User clicks submit button
        Then User record is updated
