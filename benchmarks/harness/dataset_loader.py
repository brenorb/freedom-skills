"""Official GEPA DataLoader protocol with globally split-qualified cache IDs."""
import re


class CaseDataLoader:
    """Preserve declared order/payload IDs, qualifying opaque GEPA IDs only.

    GEPA's evaluation cache is shared by train and validation loaders. Its
    default list loaders both start at integer zero, so independent lists must
    not be passed when cache_evaluation=True.
    """
    def __init__(self, namespace, cases):
        if not isinstance(namespace,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',namespace):
            raise ValueError('A nonempty single-component split namespace is required')
        self._items={}
        for case in cases:
            case_id=case.get('id')
            if not isinstance(case_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',case_id):
                raise ValueError('Case IDs must be nonempty single components')
            key=namespace+'/'+case_id
            if key in self._items:raise ValueError('Duplicate case ID: '+key)
            self._items[key]=dict(case)
        if not self._items:raise ValueError('Search datasets must be nonempty')
        self._ids=tuple(self._items)

    def all_ids(self):
        return self._ids

    def fetch(self, ids):
        return [self._items[key] for key in ids]

    def __len__(self):
        return len(self._ids)


def search_loaders(training,validation):
    train=CaseDataLoader('train',training)
    val=CaseDataLoader('validation',validation)
    if set(train.all_ids()) & set(val.all_ids()):
        raise ValueError('Training and validation GEPA IDs must be disjoint')
    return train,val
