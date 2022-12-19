Feature: Viewing a post

    Scenario: User views a post
        Given a post exists
        When user visits the correct url
        Then the post can be viewed