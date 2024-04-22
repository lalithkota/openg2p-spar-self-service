from openg2p_fastapi_common.service import BaseService
from openg2p_fastapi_auth.models.credentials import AuthCredentials

import orjson
import re
from typing import List
from ..schemas import (
    KeyValuePair,
    Fa,
)
from ..models import Strategy, LoginProvider
from ..schemas import STRATEGY_ID_KEY


class StrategyHelper(BaseService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _construct(self, values: List[KeyValuePair], strategy: str) -> str:
        return strategy.format(
            **{key_value.key: key_value.value for key_value in values}
        )

    def _deconstruct(self, value: str, strategy: str) -> List[KeyValuePair]:
        """
        Deconstructs a value string using the provided regex strategy, returning key-value pairs.
        """
        regex_res = re.match(strategy, value)
        if regex_res:
            regex_res = regex_res.groupdict()
            return [KeyValuePair(key=k, value=v) for k, v in regex_res.items()]
        return []

    async def construct_id(
        self,
        auth: AuthCredentials,
    ) -> str:

        login_provider: LoginProvider = await LoginProvider.get_login_provider_from_iss(
            auth.iss
        )
        constructed_id = self._construct(
            [
                KeyValuePair(
                    key=key,
                    value=(
                        value
                        if isinstance(value, str)
                        else orjson.dumps(value).decode()
                    ),
                )
                for key, value in auth.model_dump().items()
            ],
            login_provider.strategy_id,
        )

        return constructed_id

    async def construct_fa(self, fa: Fa) -> str:
        strategy = await Strategy.get_strategy(
            id=fa.strategy_id,
        )
        constructed_fa = self._construct(
            [
                KeyValuePair(
                    key=key,
                    value=(
                        value
                        if isinstance(value, str)
                        else orjson.dumps(value).decode()
                    ),
                )
                for key, value in fa.dict().items()
            ],
            strategy.construct_strategy,
        )
        return constructed_fa

    async def deconstruct_fa(self, fa: str, additional_info: List[dict]) -> Fa:
        """
        Deconstructs the 'fa' string based on a strategy obtained from additional_info where the
        key is 'strategy_id'. Returns an instance of Fa filled with deconstructed values.
        """
        strategy_id = next(
            (
                info["value"]
                for info in additional_info
                if info["key"] == STRATEGY_ID_KEY
            ),
            None,
        )
        if strategy_id:
            strategy = await Strategy.get_strategy(
                id=strategy_id,
            )
            if strategy:
                deconstructed_pairs = self._deconstruct(
                    fa, strategy.deconstruct_strategy
                )
                deconstructed_fa = Fa(
                    **{pair.key: pair.value for pair in deconstructed_pairs}
                )
                return deconstructed_fa
        return Fa()
