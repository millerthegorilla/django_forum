Feature: Viewing a post
    
    Scenario: User views a post
        Given User is logged in
        And A post exists
        When User visits the post view page
        Then The post can be viewed