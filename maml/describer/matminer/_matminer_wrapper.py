"""
Wrapper for matminer featurizers
"""

from inspect import signature
import logging
from typing import Any, Callable, Optional

import pandas as pd

from maml.base import BaseDescriber

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def wrap_matminer_describer(cls_name: str, wrapped_class: Any,
                            obj_conversion: Callable,
                            describer_type: Optional[Any] = None):
    """
    Wrapper of matminer describers.
    Args:
        cls_name (str): new class name
        wrapped_class (class object): matminer BaseFeaturizer
        obj_conversion (callable): function to convert objects into desired
            object type within transform_one
        describer_type (object): object type

    Returns: maml describer class
    """

    def constructor(self, *args, **kwargs):
        """
        Wrapped __init__ constructor
        """
        n_jobs = kwargs.pop("n_jobs", 0)
        memory = kwargs.pop("memory", None)
        verbose = kwargs.pop("verbose", False)
        feature_batch = kwargs.pop("feature_concat", "pandas_concat")
        wrapped_class.__init__(self, *args, **kwargs)
        logger.info(f"Using matminer {wrapped_class.__name__} class")
        base_kwargs = dict(n_jobs=n_jobs, memory=memory,
                           verbose=verbose, feature_batch=feature_batch)
        super(new_class, self).__init__(**base_kwargs)

    @classmethod  # type: ignore
    def _get_param_names(cls):  # type: ignore
        return wrapped_class._get_param_names()

    def get_params(self, deep=False):
        params = wrapped_class.get_params(self, deep=deep)
        return params

    def transform_one(self, obj: Any):
        """
        featurize to transform_one
        """
        obj = obj_conversion(obj)
        results = wrapped_class.featurize(self, obj)
        labels = wrapped_class.feature_labels(self)
        return pd.DataFrame({i: [j] for i, j in zip(labels, results)})

    @classmethod  # type: ignore
    def from_preset(cls, name: str, **kwargs):  # type: ignore
        """
        Wrap matminer's from_preset function
        """
        instance = wrapped_class.from_preset(name)
        sig = signature(wrapped_class.__init__)
        args = list(sig.parameters.keys())[1:]
        params = {i: None for i in args}
        params.update(**kwargs)
        instance_new = cls(**params)
        instance_new.__dict__.update(instance.__dict__)
        return instance_new

    new_class = type(cls_name, (BaseDescriber, ),
                     {'__doc__': wrapped_class.__doc__,
                      '__init__': constructor,
                      '__str__': wrapped_class.__str__,
                      '__repr__': wrapped_class.__repr__,
                      '__getstate__': wrapped_class.__getstate__,
                      '__setstate__': wrapped_class.__setstate__,
                      '_get_param_names': _get_param_names,
                      'transform_one': transform_one,
                      'from_preset': from_preset,
                      'get_params': get_params,
                      '__module__': 'maml.describer',
                      'describer_type': describer_type
                      })

    return new_class
