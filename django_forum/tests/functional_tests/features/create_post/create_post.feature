
Feature: Creating a post
    
    @locutus
    Scenario: User creates a post
        Given User is logged in
        When User is on the create post page
        And User enters some text
        And User clicks the save button
        Then Post is stored in database
        And User is taken to post detail page