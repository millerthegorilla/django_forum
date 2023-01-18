Feature: Subscribing to posts

    Scenario: User subscribes to a post
        Given User is logged in
        And A post exists
        When User visits the post view page
        And User clicks subscribe checkbox
        And Browser is refreshed
        Then Subscribe checkbox is checked
        And User is subscribed


    Scenario: Subscribe checkbox is checked
        Given User is logged in
        And A post exists
        And User is subscribed
        When User visits the post view page
        Then Subscribe checkbox is checked


    Scenario: User unsubscribes from a post    
        Given User is logged in
        And A post exists
        And User is subscribed
        When User visits the post view page
        And Subscribe checkbox is checked
        And User clicks subscribe checkbox
        And Browser is refreshed
        Then User is not subscribed
        And Subscribe checkbox is not checked


    Scenario:  User creates a comment on a post that is subscribed
        Given Other user is logged in
        And A post exists
        When Other user visits the post view page
        And User is subscribed
        And Other user creates a comment
        Then A task is scheduled
