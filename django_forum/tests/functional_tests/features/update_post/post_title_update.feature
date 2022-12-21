Feature: Update post title

    Scenario: User updates the post title
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User clicks the edit post button
        Then The title is editable
        And User changes the post title
        And User clicks the save button
        Then The updated post title is saved
        And User is redirected to view post page