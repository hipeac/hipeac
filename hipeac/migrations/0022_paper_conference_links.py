# Generated by Django 4.2.6 on 2023-11-06 11:39

from django.db import migrations


def url_to_links(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    PublicationConference = apps.get_model("hipeac", "PublicationConference")
    Link = apps.get_model("hipeac", "Link")

    for conference in PublicationConference.objects.all():
        ct = ContentType.objects.get_for_model(PublicationConference)

        if conference.url:
            Link.objects.create(
                content_type=ct,
                object_id=conference.id,
                type="dblp",
                url=conference.url,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0021_acacesgrant_available_places"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="webinar",
            options={"ordering": ["start_at"]},
        ),
        # -----
        migrations.RunPython(url_to_links),
        # -----
        migrations.RemoveField(
            model_name="publicationconference",
            name="url",
        ),
    ]
