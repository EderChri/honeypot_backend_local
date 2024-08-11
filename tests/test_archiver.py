from utils.structures import Message, Conversation


def test_archive_message_with_unique_id(archiver, mocked_writer):
    scam_id = "scam123"
    message = Message(is_inbound=True, from_addr="sender", to_addr="receiver", time=1625247600, medium="Email",
                      body="Test message")

    archiver.archive_message(scam_id, message, is_unique_id=True)

    mocked_writer.add_message.assert_called_once_with(scam_id, message)


def test_archive_message_without_unique_id(archiver, mocked_loader, mocked_writer):
    scam_id = "scam123"
    message = Message(is_inbound=True, from_addr="sender", to_addr="receiver", time=1625247600, medium="Email",
                      body="Test message")
    unique_scam_id = "unique_scam_id"

    mocked_loader.get_unique_scam_id.return_value = unique_scam_id

    archiver.archive_message(scam_id, message, is_unique_id=False)

    mocked_loader.get_unique_scam_id.assert_called_once_with(scam_id)
    mocked_writer.add_message.assert_called_once_with(unique_scam_id, message)


def test_archive_conversation(archiver, mocked_writer):
    conversation = Conversation(unique_scam_id="conv123", scam_ids={}, victim_ids={}, pause_start=0, pause_end=0,
                                already_queued=False, victim_name="victim")

    archiver.archive_conversation(conversation)

    mocked_writer.write_conversation.assert_called_once_with(conversation)
