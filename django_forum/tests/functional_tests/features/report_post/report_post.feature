Feature: Reporting a post

    Scenario: User can see moderation link
        Given Other user is logged in
        And A post exists
        When User visits the post view page
        Then Moderation link is visible


    Scenario: User can report post for moderation
        Given Other user is logged in
        And A post exists
        When User visits the post view page
        And Moderation link is visible
        And User clicks the moderation link
        Then Moderation message is visible
        And Post has a moderation date
        And Comments are locked