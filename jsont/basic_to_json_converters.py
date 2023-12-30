from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Mapping, Sequence, TypeVar, get_args

from jsont.base_types import Json, JsonNull, JsonSimple

T = TypeVar("T")


class ToJsonConverter(ABC, Generic[T]):
    """The base-class for converters that convert to objects representing json.

    Converters that convert objects of their specific type `T` to objects representing json have to
    implement the two abstract methods defined in this base-class.
    """

    @abstractmethod
    def can_convert(self, o: Any) -> bool:
        """Return if this converter can convert the given object to an object representing json.

        Args:
            o: the object to be converted to an object representing json
        Returns:
            `true` if this converter can convert the given object into an object representing json,
            `false` otherwise.
        """

    @abstractmethod
    def convert(self, o: T, to_json: Callable[[Any], Json]) -> Json:
        """Convert the given object of type `T` to an object representing json.

        Args:
            o: the object to convert
            to_json: If this converter converts container types like :class:`typing.Sequence`
                this function is used to convert the contained objects into their corresponding
                objects representing json.
        Returns:
            the converted object representing json.
        Raises:
            ValueError: If the object cannot be converted to an object representing json.
        """


class FromNone(ToJsonConverter[JsonNull]):
    """Converts a `None` instance.

    A `None` is converted to `None`.
    """

    def can_convert(self, o: Any) -> bool:
        return o is None

    def convert(self, o: JsonNull, to_json: Callable[[Any], Json]) -> JsonNull:
        return None


class FromSimple(ToJsonConverter[JsonSimple]):
    """Converts simple objects of type `int`, `float`, `str`, `bool`.

    The conversion simply returns the given object.
    """

    def can_convert(self, o: Any) -> bool:
        return isinstance(o, get_args(JsonSimple))

    def convert(self, o: JsonSimple, to_json: Callable[[Any], Json]) -> JsonSimple:
        return o


class FromSequence(ToJsonConverter[Sequence[Any]]):
    """Converts :objects of type class:`typing.Sequence`.

    A `Sequence` is converted to a `list` with all elements being converted with their
    respective :class:`ToJsonConverter`.
    """

    def can_convert(self, o: Any) -> bool:
        return isinstance(o, Sequence)

    def convert(self, o: Sequence[Any], to_json: Callable[[Any], Json]) -> Json:
        return [to_json(e) for e in o]


class FromMapping(ToJsonConverter[Mapping[Any, Any]]):
    """Converts :objects of type class:`typing.Mapping`.

    A `Mapping` with `str` types keys is converted to a `dict` with all values being converted
    with their respective :class:`ToJsonConverter`.
    """

    def can_convert(self, o: Any) -> bool:
        return isinstance(o, Mapping)

    def convert(self, o: Mapping[Any, Any], to_json: Callable[[Any], Json]) -> Json:
        """Convert the given object of type :class:`typing.Mapping` to an object representing json.

        Raises:
            ValueError: If the :class:`typing.Mapping` contains none-`str` keys.
        """

        def ensure_str(k: Any) -> str:
            if isinstance(k, str):
                return k
            raise ValueError(f"Cannot convert {o} to json as it contains a non-str key: {k}")

        return {ensure_str(k): to_json(v) for k, v in o.items()}