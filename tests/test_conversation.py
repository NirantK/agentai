import pytest

from agentai.conversation import Conversation, Message


@pytest.fixture
def conversation():
    '''Returns a Conversation object'''
    return Conversation()


def test_add_message(conversation):
    '''Tests the add_message method of the Conversation class'''
    conversation.add_message("User", "Hello")
    assert conversation.history == [Message(role="User", content="Hello", name=None)]
    conversation.history.pop()  # Rollback the addition of the message
    assert conversation.history == []  # Ensure that the conversation history is empty


def test_add_message_with_name(conversation):
    '''Tests the add_message method of the Conversation class with an Optional name'''
    conversation.add_message("Assistant", "Hi there!", "AI")
    assert conversation.history == [Message(role="Assistant", content="Hi there!", name="AI")]
    conversation.history.pop()  # Rollback the addition of the message
    assert conversation.history == []  # Ensure that the conversation history is empty


def test_get_history(conversation):
    '''Tests the get_history method of the Conversation class'''
    conversation.add_message("User", "Hello!")
    conversation.add_message("Assistant", "Hi there!")
    conversation.add_message("User", "How are you?")
    conversation.add_message("Assistant", "I'm doing well, thank you!")
    conversation.add_message("User", "That's great to hear!")
    conversation.add_message("Assistant", "Thank you! How can I assist you today?")
    conversation.add_message("User", "I have a recipe conundrum. I want to make something special for dinner.")
    conversation.add_message("Assistant", "That sounds fun! What type of cuisine are you interested in?")
    conversation.add_message("User", "I'd like to try making a Thai dish.")
    conversation.add_message(
        "Assistant",
        "Excellent choice! How about trying to make Pad Thai? It's a popular Thai noodle dish.",
    )
    conversation.add_message("User", "Pad Thai sounds delicious! Do you have a recipe?")
    conversation.add_message(
        "Assistant",
        "Certainly! Here's a simple Pad Thai recipe for you:\n\nIngredients:\n- Rice noodles\n- Tofu or your choice of protein\n- Eggs\n- Bean sprouts\n- Chopped green onions\n- Chopped peanuts\n- Lime wedges\n- Pad Thai sauce (made from tamarind paste, fish sauce, sugar, and chili flakes)\n\nInstructions:\n1. Soak the rice noodles in warm water until they soften. Drain and set aside.\n2. In a wok or large pan, stir-fry the tofu or protein until cooked. Push it to one side of the pan.\n3. Crack the eggs into the pan and scramble them until they're nearly cooked.\n4. Add the softened rice noodles to the pan and pour the Pad Thai sauce over them.\n5. Toss everything together until the noodles are coated in the sauce.\n6. Add bean sprouts and chopped green onions, continuing to stir-fry until they're tender.\n7. Serve hot, garnished with chopped peanuts and lime wedges.\n\nEnjoy your Pad Thai!",
    )
    conversation.add_message("User", "Wow, thank you! I can't wait to try making it.")
    conversation.add_message(
        "Assistant",
        "You're welcome! Cooking can be a delightful experience. If you have any more questions or need assistance with anything else, feel free to ask.",
    )
    conversation.add_message("User", "Sure thing! By the way, what's the weather like today?")
    conversation.add_message(
        "Assistant",
        "I apologize, but as an AI language model, I don't have access to real-time data, including weather updates. You can check the weather forecast on a reliable website or a weather app for accurate information.",
    )
    conversation.add_message("User", "No problem. I have another question then. Can you tell me a joke?")
    conversation.add_message(
        "Assistant",
        "Of course! Here's one for you: Why don't scientists trust atoms? Because they make up everything!",
    )
    conversation.add_message("User", "Haha, that's a good one! I needed that laugh. Thanks!")
    conversation.add_message(
        "Assistant",
        "You're welcome! Laughter is the best medicine. If you ever need more jokes or anything else, I'm here to brighten your day!",
    )
    conversation.add_message(
        "User",
        "That's very kind of you. Actually, I've been feeling a bit stressed lately.",
    )
    conversation.add_message(
        "Assistant",
        "I'm sorry to hear that. Stress can be challenging to deal with. Is there something specific bothering you, or do you need some general tips to manage stress?",
    )
    conversation.add_message("User", "I'd appreciate some tips on how to manage stress.")
    conversation.add_message(
        "Assistant",
        "Of course! Here are some helpful tips:\n1. Practice deep breathing or meditation to relax your mind and body.\n2. Engage in physical activities like walking, jogging, or yoga to release endorphins.\n3. Take breaks and do something you enjoy, like reading, listening to music, or spending time in nature.\n4. Prioritize your tasks and break them into smaller, manageable steps.\n5. Reach out to friends or family for support and talk about what's on your mind.\n6. Get enough sleep to allow your body to recover and rejuvenate.\n7. Consider trying relaxation techniques like progressive muscle relaxation or visualization.\n8. Limit caffeine and alcohol consumption, as they can increase stress levels.\n9. Learn to say no to tasks or commitments when you feel overwhelmed.\n10. Seek professional help if you find that stress is significantly affecting your daily life.\n\nRemember, it's essential to take care of yourself, and don't hesitate to seek support when needed.",
    )
    conversation.add_message("User", "Thank you for the wonderful advice. I'll definitely give these tips a try.")
    conversation.add_message(
        "Assistant",
        "You're welcome! I hope these tips help you find some relief from stress. If you have any more questions or need further assistance, don't hesitate to ask. Take care!",
    )
    conversation.add_message("User", "I appreciate that. Take care too!")
    conversation.add_message("Assistant", "Thank you! Have a fantastic day!")
    assert conversation.get_history() == [
        Message(role="User", content="Hello!", name=None),
        Message(role="Assistant", content="Hi there!", name=None),
        Message(role="User", content="How are you?", name=None),
        Message(role="Assistant", content="I'm doing well, thank you!", name=None),
        Message(role="User", content="That's great to hear!", name=None),
        Message(role="Assistant", content="Thank you! How can I assist you today?", name=None),
        Message(
            role="User", content="I have a recipe conundrum. I want to make something special for dinner.", name=None
        ),
        Message(role="Assistant", content="That sounds fun! What type of cuisine are you interested in?", name=None),
        Message(role="User", content="I'd like to try making a Thai dish.", name=None),
        Message(
            role="Assistant",
            content="Excellent choice! How about trying to make Pad Thai? It's a popular Thai noodle dish.",
            name=None,
        ),
        Message(role="User", content="Pad Thai sounds delicious! Do you have a recipe?", name=None),
        Message(
            role="Assistant",
            content="Certainly! Here's a simple Pad Thai recipe for you:\n\nIngredients:\n- Rice noodles\n- Tofu or your choice of protein\n- Eggs\n- Bean sprouts\n- Chopped green onions\n- Chopped peanuts\n- Lime wedges\n- Pad Thai sauce (made from tamarind paste, fish sauce, sugar, and chili flakes)\n\nInstructions:\n1. Soak the rice noodles in warm water until they soften. Drain and set aside.\n2. In a wok or large pan, stir-fry the tofu or protein until cooked. Push it to one side of the pan.\n3. Crack the eggs into the pan and scramble them until they're nearly cooked.\n4. Add the softened rice noodles to the pan and pour the Pad Thai sauce over them.\n5. Toss everything together until the noodles are coated in the sauce.\n6. Add bean sprouts and chopped green onions, continuing to stir-fry until they're tender.\n7. Serve hot, garnished with chopped peanuts and lime wedges.\n\nEnjoy your Pad Thai!",
            name=None,
        ),
        Message(role="User", content="Wow, thank you! I can't wait to try making it.", name=None),
        Message(
            role="Assistant",
            content="You're welcome! Cooking can be a delightful experience. If you have any more questions or need assistance with anything else, feel free to ask.",
            name=None,
        ),
        Message(role="User", content="Sure thing! By the way, what's the weather like today?", name=None),
        Message(
            role="Assistant",
            content="I apologize, but as an AI language model, I don't have access to real-time data, including weather updates. You can check the weather forecast on a reliable website or a weather app for accurate information.",
            name=None,
        ),
        Message(role="User", content="No problem. I have another question then. Can you tell me a joke?", name=None),
        Message(
            role="Assistant",
            content="Of course! Here's one for you: Why don't scientists trust atoms? Because they make up everything!",
            name=None,
        ),
        Message(role="User", content="Haha, that's a good one! I needed that laugh. Thanks!", name=None),
        Message(
            role="Assistant",
            content="You're welcome! Laughter is the best medicine. If you ever need more jokes or anything else, I'm here to brighten your day!",
            name=None,
        ),
        Message(
            role="User",
            content="That's very kind of you. Actually, I've been feeling a bit stressed lately.",
            name=None,
        ),
        Message(
            role="Assistant",
            content="I'm sorry to hear that. Stress can be challenging to deal with. Is there something specific bothering you, or do you need some general tips to manage stress?",
            name=None,
        ),
        Message(role="User", content="I'd appreciate some tips on how to manage stress.", name=None),
        Message(
            role="Assistant",
            content="Of course! Here are some helpful tips:\n1. Practice deep breathing or meditation to relax your mind and body.\n2. Engage in physical activities like walking, jogging, or yoga to release endorphins.\n3. Take breaks and do something you enjoy, like reading, listening to music, or spending time in nature.\n4. Prioritize your tasks and break them into smaller, manageable steps.\n5. Reach out to friends or family for support and talk about what's on your mind.\n6. Get enough sleep to allow your body to recover and rejuvenate.\n7. Consider trying relaxation techniques like progressive muscle relaxation or visualization.\n8. Limit caffeine and alcohol consumption, as they can increase stress levels.\n9. Learn to say no to tasks or commitments when you feel overwhelmed.\n10. Seek professional help if you find that stress is significantly affecting your daily life.\n\nRemember, it's essential to take care of yourself, and don't hesitate to seek support when needed.",
            name=None,
        ),
        Message(
            role="User", content="Thank you for the wonderful advice. I'll definitely give these tips a try.", name=None
        ),
        Message(
            role="Assistant",
            content="You're welcome! I hope these tips help you find some relief from stress. If you have any more questions or need further assistance, don't hesitate to ask. Take care!",
            name=None,
        ),
        Message(role="User", content="I appreciate that. Take care too!", name=None),
        Message(role="Assistant", content="Thank you! Have a fantastic day!", name=None),
    ]


def test_trim_history():
    ''' Test to check that the trimmed history is correct.
    model = 'gpt3.5-turbo' and max_history_tokens = 200 '''
    conversation_with_tokens = Conversation(max_history_tokens=200, model="gpt-3.5-turbo")
    conversation_with_tokens.add_message("User", "Hello!")
    conversation_with_tokens.add_message("Assistant", "Hi there!")
    conversation_with_tokens.add_message("User", "How are you?")
    conversation_with_tokens.add_message("Assistant", "I'm doing well, thank you!")
    conversation_with_tokens.add_message("User", "That's great to hear!")
    conversation_with_tokens.add_message("Assistant", "Thank you! How can I assist you today?")
    conversation_with_tokens.add_message(
        "User", "I have a recipe conundrum. I want to make something special for dinner."
    )
    conversation_with_tokens.add_message("Assistant", "That sounds fun! What type of cuisine are you interested in?")
    conversation_with_tokens.add_message("User", "I'd like to try making a Thai dish.")
    conversation_with_tokens.add_message(
        "Assistant",
        "Excellent choice! How about trying to make Pad Thai? It's a popular Thai noodle dish.",
    )
    conversation_with_tokens.add_message("User", "Pad Thai sounds delicious! Do you have a recipe?")
    conversation_with_tokens.add_message(
        "Assistant",
        "Certainly! Here's a simple Pad Thai recipe for you:\n\nIngredients:\n- Rice noodles\n- Tofu or your choice of protein\n- Eggs\n- Bean sprouts\n- Chopped green onions\n- Chopped peanuts\n- Lime wedges\n- Pad Thai sauce (made from tamarind paste, fish sauce, sugar, and chili flakes)\n\nInstructions:\n1. Soak the rice noodles in warm water until they soften. Drain and set aside.\n2. In a wok or large pan, stir-fry the tofu or protein until cooked. Push it to one side of the pan.\n3. Crack the eggs into the pan and scramble them until they're nearly cooked.\n4. Add the softened rice noodles to the pan and pour the Pad Thai sauce over them.\n5. Toss everything together until the noodles are coated in the sauce.\n6. Add bean sprouts and chopped green onions, continuing to stir-fry until they're tender.\n7. Serve hot, garnished with chopped peanuts and lime wedges.\n\nEnjoy your Pad Thai!",
    )
    conversation_with_tokens.add_message("User", "Wow, thank you! I can't wait to try making it.")
    conversation_with_tokens.add_message(
        "Assistant",
        "You're welcome! Cooking can be a delightful experience. If you have any more questions or need assistance with anything else, feel free to ask.",
    )
    conversation_with_tokens.add_message("User", "Sure thing! By the way, what's the weather like today?")
    conversation_with_tokens.add_message(
        "Assistant",
        "I apologize, but as an AI language model, I don't have access to real-time data, including weather updates. You can check the weather forecast on a reliable website or a weather app for accurate information.",
    )
    conversation_with_tokens.add_message("User", "No problem. I have another question then. Can you tell me a joke?")
    conversation_with_tokens.add_message(
        "Assistant",
        "Of course! Here's one for you: Why don't scientists trust atoms? Because they make up everything!",
    )
    conversation_with_tokens.add_message("User", "Haha, that's a good one! I needed that laugh. Thanks!")
    conversation_with_tokens.add_message(
        "Assistant",
        "You're welcome! Laughter is the best medicine. If you ever need more jokes or anything else, I'm here to brighten your day!",
    )
    conversation_with_tokens.add_message(
        "User",
        "That's very kind of you. Actually, I've been feeling a bit stressed lately.",
    )
    conversation_with_tokens.add_message(
        "Assistant",
        "I'm sorry to hear that. Stress can be challenging to deal with. Is there something specific bothering you, or do you need some general tips to manage stress?",
    )
    conversation_with_tokens.add_message("User", "I'd appreciate some tips on how to manage stress.")
    conversation_with_tokens.add_message(
        "Assistant",
        "Of course! Here are some helpful tips:\n1. Practice deep breathing or meditation to relax your mind and body.\n2. Engage in physical activities like walking, jogging, or yoga to release endorphins.\n3. Take breaks and do something you enjoy, like reading, listening to music, or spending time in nature.\n4. Prioritize your tasks and break them into smaller, manageable steps.\n5. Reach out to friends or family for support and talk about what's on your mind.\n6. Get enough sleep to allow your body to recover and rejuvenate.\n7. Consider trying relaxation techniques like progressive muscle relaxation or visualization.\n8. Limit caffeine and alcohol consumption, as they can increase stress levels.\n9. Learn to say no to tasks or commitments when you feel overwhelmed.\n10. Seek professional help if you find that stress is significantly affecting your daily life.\n\nRemember, it's essential to take care of yourself, and don't hesitate to seek support when needed.",
    )
    conversation_with_tokens.add_message(
        "User", "Thank you for the wonderful advice. I'll definitely give these tips a try."
    )
    conversation_with_tokens.add_message(
        "Assistant",
        "You're welcome! I hope these tips help you find some relief from stress. If you have any more questions or need further assistance, don't hesitate to ask. Take care!",
    )
    conversation_with_tokens.add_message("User", "I appreciate that. Take care too!")
    conversation_with_tokens.add_message("Assistant", "Thank you! Have a fantastic day!")

    # Get the trimmed history that is limited by tokens
    # and store it in a variable called trimmed_history
    trimmed_history = conversation_with_tokens.get_history(trimmed=True)

    # Check that the trimmed history is not empty
    assert trimmed_history is not None

    # Check if the trimmed history doesn't contain the first message
    assert trimmed_history[0] != Message(role="User", content="Hello!", name=None)

    # Check the length of the trimmed history
    # It should be 4 when the max_history_tokens is set to 200 with the model gpt-3.5-turbo
    assert len(trimmed_history) == 4

    # check that the trimmed history is correct

    assert trimmed_history == [
        Message(
            role="User", content="Thank you for the wonderful advice. I'll definitely give these tips a try.", name=None
        ),
        Message(
            role="Assistant",
            content="You're welcome! I hope these tips help you find some relief from stress. If you have any more questions or need further assistance, don't hesitate to ask. Take care!",
            name=None,
        ),
        Message(role="User", content="I appreciate that. Take care too!", name=None),
        Message(role="Assistant", content="Thank you! Have a fantastic day!", name=None),
    ]


def test_missing_params():
    '''Test to check that the ValueError is raised when max_history_tokens or model is not set when trim_history is called'''
    conversation = Conversation()
    with pytest.raises(ValueError):
        conversation.trim_history()