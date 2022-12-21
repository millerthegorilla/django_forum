Feature: Update post text

    Scenario: User updates the post text
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User clicks the edit post button
        Then tinymce is displayed
        And User changes the post text
        And User clicks the save button
        And The updated post text is saved
        And User is redirected to view post page
