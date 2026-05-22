from pkg.models import NewOllamaModel,NewClaudeAiModel
from pkg.config import Initialize
import threading
from pkg import cache
from pkg.service import LLMService   
import asyncio
from pkg.util import usage
from pkg.util import connection
def Start():
    """Main function to start the server"""
    try:
        slog,config = Initialize()
        slog.info
        app =  connection.Router()

        monitor_thread = threading.Thread(target=usage.Log_system_usage,args=(slog, 120),daemon=True)
        monitor_thread.start()

        # Setup logging
        slog.info(f"Initializing gRPC server,{config.app.models.mcp}")
        mcp = cache.MCPManager(client=connection.MCPClient(config.app.models.mcp.base_url))
        model = NewOllamaModel(cfg=config,mcp=mcp)
        slog.info(f"found available ,models {model.get_available_models()}")
        try:
            methods = asyncio.run(mcp.Get_tools_schema())
            slog.info(f"Available MCP methods: {methods}")
            response = model.GetResponse("give summary of alarm of this 01 march 2026 to 23 march 2026 and asset code is 55A and consider the organization id is bt1-lab","llama3")
            slog.info(f"model response is: {response}")
        except Exception:
            slog.info(f"MCP attributes: {dir(mcp)}")


        

    except Exception as e:
        slog.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise



