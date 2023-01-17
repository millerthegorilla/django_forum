Feature: Reporting a comment

    Scenario: User can see moderation link
        Given Other user is logged in
        And A post exists
        And A comment exists
        When User visits the post view page
        Then Moderation link is visible

    Scenario: User can report comment for moderation
        Given Other user is logged in
        And A post exists
        And A comment exists
        When User visits the post view page
        And Comment moderation link is visible
        And User clicks the moderation link
        Then Moderation message is visible
        And comment has a moderation date
