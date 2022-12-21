Feature: Listing posts

    Scenario: User lists all posts
        Given User is logged in
        And A post exists
        When User visits the post list page
        Then The post is listed