Feature: Update comment text

    Scenario: User updates the comment text
        Given User is logged in
        And A post exists
        And A comment exists
        When User visits the post view page
        And User clicks the edit comment link
        Then Textarea is displayed
        And User changes the comment text
        And User clicks the save link
        And The updated comment text is saved
