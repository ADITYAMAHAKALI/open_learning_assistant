# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User

from app.adapters.llm.base import LLMClient
from app.adapters.llm.ollama_provider import OllamaClient
from app.adapters.llm.gemini_provider import GeminiClient

from app.adapters.vectorstore.opensearch_client import get_opensearch_client
from app.adapters.vectorstore.opensearch_vectorstore import OpenSearchVectorStore

from app.adapters.storage.object_storage import StorageBackend, LocalFileStorage

from app.services.rag_service import RAGService
from app.services_impl.rag_service_opensearch_impl import RAGServiceOpenSearchImpl

from app.services.materials_service import MaterialsService
from app.services_impl.materials_service_impl import MaterialsServiceImpl

from app.services.auth_service import AuthService
from app.services_impl.auth_service_impl import AuthServiceImpl

from app.services.prereq_service import PrereqService
from app.services_impl.prereq_llm_impl import PrereqLLMImpl

from app.services.session_service import SessionService
from app.services_impl.session_service_impl import SessionServiceImpl

from app.adapters.wiki.wikipedia_client import WikipediaClient


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_llm_client() -> LLMClient:
    if settings.LLM_PROVIDER == "gemini":
        return GeminiClient(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
        )
    else:
        # default ollama
        return OllamaClient(
            base_url=str(settings.OLLAMA_BASE_URL),
            model=settings.OLLAMA_MODEL,
        )


def get_vector_store() -> OpenSearchVectorStore:
    client = get_opensearch_client()
    return OpenSearchVectorStore(
        client=client,
        index_name=settings.OPENSEARCH_INDEX,
    )


def get_storage_backend() -> StorageBackend:
    # later you can branch on STORAGE_BACKEND == "s3" | "minio"
    return LocalFileStorage()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthServiceImpl(db=db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        sub = payload.get("sub")
        token_type = payload.get("type")
        if sub is None or token_type != "access":
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


def get_rag_service(
    db: Session = Depends(get_db),
    vector_store: OpenSearchVectorStore = Depends(get_vector_store),
    llm: LLMClient = Depends(get_llm_client),
) -> RAGService:
    return RAGServiceOpenSearchImpl(
        db=db,
        vector_store=vector_store,
        llm=llm,
    )


def get_materials_service(
    db: Session = Depends(get_db),
    vector_store: OpenSearchVectorStore = Depends(get_vector_store),
    storage: StorageBackend = Depends(get_storage_backend),
) -> MaterialsService:
    return MaterialsServiceImpl(
        db=db,
        vector_store=vector_store,
        storage=storage,
    )


def get_wikipedia_client() -> WikipediaClient:
    return WikipediaClient()


def get_prereq_service(
    llm: LLMClient = Depends(get_llm_client),
) -> PrereqService:
    return PrereqLLMImpl(llm=llm)


def get_session_service(
    db: Session = Depends(get_db),
    prereq_service: PrereqService = Depends(get_prereq_service),
    wiki_client: WikipediaClient = Depends(get_wikipedia_client),
) -> SessionService:
    return SessionServiceImpl(
        db=db,
        prereq_service=prereq_service,
        wiki_client=wiki_client,
    )
