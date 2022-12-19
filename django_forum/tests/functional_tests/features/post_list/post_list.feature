Feature: Listing posts

    Scenario: User lists all posts
        Given A post exists
        When User visits the post list page
        Then the post is listed