# pkg/service/llm_service.py

import predictor_pb2
import predictor_pb2_grpc


class LLMService(predictor_pb2_grpc.LLMServiceServicer):

    def __init__(self):
        self.registry = None
        self.executor = None

    def _init_models(self, model_map):
        from pkg.service.registry import ModelRegistry
        from pkg.service.executor import LLMExecutor

        self.registry = ModelRegistry()

        for model_type, instance in model_map.items():
            self.registry.register(model_type, instance)

        self.executor = LLMExecutor(self.registry)

    def ChatStream(self, request, context):
        try:
            for chunk in self.executor.stream(request):
                yield predictor_pb2.ChatResponse(
                    session_id=request.session_id,
                    request_id=request.request_id,
                    content=chunk,
                    model_type=request.model_type,
                    done=False
                )

            yield predictor_pb2.ChatResponse(
                session_id=request.session_id,
                request_id=request.request_id,
                content="",
                model_type=request.model_type,
                done=True
            )

        except Exception as e:
            yield predictor_pb2.ChatResponse(
                session_id=request.session_id,
                request_id=request.request_id,
                content=str(e),
                model_type=request.model_type,
                done=True
            )