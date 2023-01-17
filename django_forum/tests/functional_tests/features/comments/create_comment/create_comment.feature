
Feature: Creating a comment
    

    Scenario: User creates a comment
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User enters some text in the comment box
        And User clicks the save button
        Then Comment is stored in database
        And User is taken to comment anchor of post detail page