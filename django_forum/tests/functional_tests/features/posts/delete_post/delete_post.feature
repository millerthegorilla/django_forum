Feature: Deleting a post

    Scenario: User deletes a post
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User clicks the delete button
        Then Post Delete modal is shown
        And User clicks the confirm button
        And Post is deleted
        And User is taken to post list page