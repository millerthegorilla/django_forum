from elasticsearch_dsl import analyzer, tokenizer, Nested
from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from .models import ForumPost, ForumComment


sugg_analyzer = analyzer('sugg_analyzer',
    tokenizer=tokenizer('trigram', 'ngram', min_gram=3, max_gram=3),
    filter=['lowercase']
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

@registry.register_document
class ForumCommentDocument(Document):

    class Index:
            # Name of the Elasticsearch index
            name = 'forum_comments_index'
            # See Elasticsearch Indices API reference for available settings
            settings = {'number_of_shards': 1,
                        'number_of_replicas': 0}

    class Django:
        """
           I no longer have an autocomplete defined, as the amount of requests is crazy.
        """

        model = ForumComment
        fields = [
            'text',
            'author',
        ]

        """
          the commented code below allows searched comments to return a post as the 'found'
          record.
        """
        # related_models = [ForumPost]

        # def get_queryset(self):
        #     return super().get_queryset().select_related(
        #         'forum_post'
        #     )


@registry.register_document
class ForumPostDocument(Document):
    text = fields.TextField(
        attr='text',
        analyzer=html_strip,
    )

    category = fields.TextField(
        attr='category_label'
    )

    location = fields.TextField(
        attr='location_label'
    )

    class Index:
            # Name of the Elasticsearch index
            name = 'forum_posts_index'
            # See Elasticsearch Indices API reference for available settings
            settings = {'number_of_shards': 1,
                        'number_of_replicas': 0}

    class Django:
        """
            I no longer have an autocomplete defined as the amount of requests goes
            through the roof.
        """

        model = ForumPost
        fields = [
             'title',
             'author',
        ]
