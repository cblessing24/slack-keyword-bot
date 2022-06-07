from slack_app.domain.model import Channel, ChannelName

from .conftest import FakeRepository


def test_sees_channel_when_adding_channel() -> None:
    repo = FakeRepository()
    channel = Channel(ChannelName("test"))
    repo.add(channel)
    assert repo.seen == {channel}


def test_sees_channel_when_getting_channel() -> None:
    channel = Channel(ChannelName("test"))
    repo = FakeRepository(channels={channel})
    repo.get(channel.channel_name)
    assert repo.seen == {channel}


def test_does_not_see_unkwnown_channel() -> None:
    repo = FakeRepository()
    repo.get(ChannelName("test"))
    assert repo.seen == set()
