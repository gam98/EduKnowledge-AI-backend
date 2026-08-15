import hashlib
import math


class DeterministicEmbeddings:
    dimension = 32

    async def embed(self, texts: list[str]) -> list[list[float]]:
        result = []
        for text in texts:
            digest = hashlib.sha256(text.encode()).digest()
            values = [digest[i % len(digest)] / 255 for i in range(self.dimension)]
            norm = math.sqrt(sum(v * v for v in values))
            result.append([v / norm for v in values])
        return result
