import pytest

from graphs.state import RecipeGraphState


@pytest.fixture
def empty_state() -> RecipeGraphState:
    """Factory for a minimal valid RecipeGraphState."""
    return RecipeGraphState(
        messages=[],
        user_query="",
        is_cooking_related=False,
        recipe_detected=False,
        recipe_text="",
        tools_used=[],
        cookware_sufficient=True,
        missing_cookware=[],
        cookware_suggestions="",
        final_response="",
        debug_log=[],
    )


@pytest.fixture
def cooking_query_state(empty_state) -> RecipeGraphState:
    """State seeded with a cooking query."""
    return {**empty_state, "user_query": "How do I make pasta carbonara?"}


@pytest.fixture
def non_cooking_query_state(empty_state) -> RecipeGraphState:
    """State seeded with an off-topic query."""
    return {**empty_state, "user_query": "Who won the Super Bowl?"}


@pytest.fixture
def recipe_state(empty_state) -> RecipeGraphState:
    """State after reasoning has produced a recipe."""
    return {
        **empty_state,
        "user_query": "How do I make pasta carbonara?",
        "is_cooking_related": True,
        "recipe_detected": True,
        "recipe_text": (
            "## Pasta Carbonara\n\n"
            "1. Boil pasta in a large pot\n"
            "2. Fry guanciale in a frying pan\n"
            "3. Mix eggs and parmesan in a mixing bowl\n"
            "4. Combine and toss\n"
        ),
        "tools_used": [],
    }


@pytest.fixture
def recipe_with_oven_state(empty_state) -> RecipeGraphState:
    """State with a recipe requiring an oven (which is missing from cookware)."""
    return {
        **empty_state,
        "user_query": "How do I bake a cake?",
        "is_cooking_related": True,
        "recipe_detected": True,
        "recipe_text": (
            "## Chocolate Cake\n\n"
            "1. Preheat oven to 350°F\n"
            "2. Mix dry ingredients in a mixing bowl\n"
            "3. Pour into baking pan\n"
            "4. Bake in oven for 30 minutes\n"
        ),
        "tools_used": [],
    }
