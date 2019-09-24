import numpy as np
import warnings
import sklearn.metrics
import tqdm


class LinkAUC:
    def __init__(self, G, nodes=None):
        self.G = G
        self.nodes = list(G) if nodes is None else list(set(list(nodes)))
        if self.G.is_directed():
            warnings.warn("LinkAUC is designed for undirected graphs", stacklevel=2)

    def _similarity(self, v, u, ranks):
        dot = 0
        l2v = 0
        l2u = 0
        for group_ranks in ranks.values():
            ui = group_ranks.get(u, 0)
            vi = group_ranks.get(v, 0)
            l2u += ui*ui
            l2v += vi*vi
            dot = ui*vi
        if l2u == 0 or l2v == 0:
            return 0
        return dot / np.sqrt(l2u*l2v)

    def evaluate(self, ranks, max_negative_samples=2000):
        negative_candidates = list(self.G)
        if len(negative_candidates) > max_negative_samples:
            negative_candidates = np.random.choice(negative_candidates, max_negative_samples)
        real = list()
        predicted = list()
        for node in tqdm.tqdm(self.nodes, desc="LinkAUC"):
            neighbors = self.G._adj[node]
            for positive in neighbors:
                real.append(1)
                predicted.append(self._similarity(node, positive, ranks))
            for negative in negative_candidates:
                if negative != node and negative not in neighbors:
                    real.append(0)
                    predicted.append(self._similarity(node, negative, ranks))
        fpr, tpr, _ = sklearn.metrics.roc_curve(real, predicted)
        return sklearn.metrics.auc(fpr, tpr)


class MultiUnsupervised:
    def __init__(self, metric_type, G):
        self.metric = metric_type(G)

    def evaluate(self, ranks):
        evaluations = [self.metric.evaluate(group_ranks) for group_ranks in ranks.values()]
        return sum(evaluations) / len(evaluations)


class MultiSupervised:
    def __init__(self, metric_type, ground_truth):
        self.metrics = {group_id: metric_type(group_truth) for group_id, group_truth in ground_truth.items()}

    def evaluate(self, ranks):
        evaluations = [self.metrics[group_id].evaluate(group_ranks) for group_id, group_ranks in ranks.items()]
        return sum(evaluations) / len(evaluations)

