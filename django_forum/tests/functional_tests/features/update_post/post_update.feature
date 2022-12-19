Feature: Update a post

    Scenario: User updates a post
        Given a post exists
        When User visits the post view page
        And User clicks the edits post button
        Then tinymce is displayed
        And User changes the post text
        And User clicks the save button
        Then the updated post is saved
        And User is redirected to view post page