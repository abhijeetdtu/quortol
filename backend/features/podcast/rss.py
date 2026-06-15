"""RSS feed serialization for podcasts."""

from __future__ import annotations

from xml.etree import ElementTree as ET

from .config import PodcastConfig
from .models import PodcastEpisode
from .repository import (
    channel_guid,
    episode_audio_canonical_url,
    episode_canonical_url,
    episode_feed_guid,
    rfc2822_datetime,
)


PODCAST_NAMESPACE = "https://podcastindex.org/namespace/1.0"
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"


def build_podcast_feed_xml(
    episodes: list[PodcastEpisode],
    config: PodcastConfig,
) -> bytes:
    ET.register_namespace("podcast", PODCAST_NAMESPACE)
    ET.register_namespace("atom", ATOM_NAMESPACE)

    root = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(root, "channel")

    ET.SubElement(channel, "title").text = config.show_title
    ET.SubElement(channel, "link").text = config.show_url
    ET.SubElement(channel, "description").text = config.show_description
    ET.SubElement(channel, "language").text = config.show_language
    ET.SubElement(channel, "generator").text = "Quortol Podcast Feed"
    ET.SubElement(channel, f"{{{PODCAST_NAMESPACE}}}medium").text = "podcast"
    ET.SubElement(channel, f"{{{PODCAST_NAMESPACE}}}guid").text = channel_guid(config)
    ET.SubElement(
        channel,
        f"{{{ATOM_NAMESPACE}}}link",
        {
            "href": config.feed_url,
            "rel": "self",
            "type": "application/rss+xml",
        },
    )

    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = config.show_image_url
    ET.SubElement(image, "title").text = config.show_title
    ET.SubElement(image, "link").text = config.show_url

    if episodes:
        last_build_source = max(
            (episode.generated_at or episode.published_at) for episode in episodes
        )
        ET.SubElement(channel, "lastBuildDate").text = rfc2822_datetime(last_build_source)

    for episode in episodes:
        item = ET.SubElement(channel, "item")
        episode_url = episode_canonical_url(episode, config)
        audio_url = episode_audio_canonical_url(episode, config)

        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "link").text = episode_url
        guid = ET.SubElement(item, "guid", {"isPermaLink": "true"})
        guid.text = episode_feed_guid(episode, config)
        ET.SubElement(item, "pubDate").text = rfc2822_datetime(episode.published_at)
        ET.SubElement(item, "description").text = episode.summary
        ET.SubElement(
            item,
            "enclosure",
            {
                "url": audio_url,
                "length": str(episode.audio_bytes),
                "type": episode.audio_mimetype,
            },
        )
        ET.SubElement(
            item,
            f"{{{PODCAST_NAMESPACE}}}transcript",
            {
                "url": episode_url,
                "type": "text/html",
            },
        )

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
