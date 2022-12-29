Feature: Subscribing to posts
    @locutus
    Scenario: User subscribes to a post
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User clicks subscribe checkbox
        And Browser is refreshed
        Then Subscribe checkbox is checked
        And User is subscribed

    @locutus
    Scenario: Subscribe checkbox is checked
        Given User is logged in
        And A post exists
        And User is subscribed
        When User visits the post view page
        Then Subscribe checkbox is checked

    @locutus
    Scenario: User unsubscribes from a post    
        Given User is logged in
        And A post exists
        And User is subscribed
        When User visits the post view page
        And User clicks subscribe checkbox
        And Browser is refreshed
        Then Subscribe checkbox is not checked
        And User is not subscribed
