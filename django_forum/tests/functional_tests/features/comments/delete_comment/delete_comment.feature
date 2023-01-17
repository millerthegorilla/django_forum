Feature: Deleting a comment

    Scenario: User deletes a comment
        Given User is logged in
        And A post exists
        And A comment exists
        When User visits the post view page
        And User clicks the delete comment link
        Then Comment delete modal is shown
        And User clicks the confirm button
        And Comment is deleted
        And User is taken to post view