Feature: Viewing a comment
    
    Scenario: User views a comment
        Given User is logged in
        And A post exists
        And A comment exists
        When User visits the post view page
        Then The comment can be viewed