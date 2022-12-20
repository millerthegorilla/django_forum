Feature: Deleting a post

    @locutus
    Scenario: User deletes a post
        Given User is logged in
        And User is on the Post View page
        And User clicks the delete button
        Then Post Delete modal is shown
        And User clicks the confirm button
        And Post is deleted
        And User is taken to post list page