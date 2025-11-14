"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { apiGet, apiPost, logout } from "@/lib/apiClient";

interface Material {
  id: number;
  filename: string;
  status: string;
}

interface SessionSummary {
  id: number;
  title: string;
  objective: string | null;
  material_count: number;
  prerequisite_count: number;
}

interface PrerequisiteNode {
  id: number;
  name: string;
  description: string | null;
  parent_id: number | null;
  wikipedia_summary: string | null;
  wikipedia_url: string | null;
}

interface SessionDetail {
  id: number;
  title: string;
  objective: string | null;
  materials: Material[];
  prerequisites: PrerequisiteNode[];
}

interface TreeNode extends PrerequisiteNode {
  children: TreeNode[];
}

const buildTree = (nodes: PrerequisiteNode[]): TreeNode[] => {
  const map = new Map<number, TreeNode>();
  nodes.forEach((node) => {
    map.set(node.id, { ...node, children: [] });
  });

  const roots: TreeNode[] = [];
  map.forEach((node) => {
    if (node.parent_id && map.has(node.parent_id)) {
      const parent = map.get(node.parent_id)!;
      parent.children.push(node);
    } else {
      roots.push(node);
    }
  });
  return roots;
};

const renderTree = (nodes: TreeNode[], depth = 0) => {
  return nodes.map((node) => (
    <div
      key={node.id}
      className="border border-neutral-200 rounded-xl p-4 bg-white/50"
      style={{ marginLeft: depth === 0 ? 0 : depth * 12 }}
    >
      <h4 className="font-medium text-sm text-neutral-900">{node.name}</h4>
      {node.description && (
        <p className="text-xs text-neutral-600 mt-1">{node.description}</p>
      )}
      {node.wikipedia_summary && (
        <p className="text-xs text-neutral-500 mt-2">
          {node.wikipedia_summary}
          {node.wikipedia_url && (
            <>
              {" "}
              <a
                href={node.wikipedia_url}
                target="_blank"
                rel="noreferrer"
                className="underline"
              >
                Wikipedia
              </a>
            </>
          )}
        </p>
      )}
      {node.children.length > 0 && (
        <div className="mt-3 space-y-3">{renderTree(node.children, depth + 1)}</div>
      )}
    </div>
  ));
};

export default function LearningPage() {
  const router = useRouter();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selectedMaterials, setSelectedMaterials] = useState<number[]>([]);
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<SessionDetail | null>(null);

  const tree = useMemo(
    () => buildTree(activeSession?.prerequisites ?? []),
    [activeSession]
  );

  const refreshMaterials = useCallback(async () => {
    const data = await apiGet("/api/v1/materials/");
    setMaterials(data);
  }, []);

  const refreshSessions = useCallback(async () => {
    const data = await apiGet("/api/v1/learning/sessions");
    setSessions(data);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        await Promise.all([refreshMaterials(), refreshSessions()]);
      } catch (err) {
        if (err instanceof Error && err.message.includes("401")) {
          setAuthError("You need to login to view your learning workspace.");
        } else if (err instanceof Error) {
          setFormError(err.message);
        }
      }
    };

    fetchData();
  }, [refreshMaterials, refreshSessions]);

  const toggleMaterial = (id: number) => {
    setSelectedMaterials((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleRefreshData = async () => {
    setFormError(null);
    try {
      await Promise.all([refreshMaterials(), refreshSessions()]);
      if (activeSession) {
        await fetchSessionDetail(activeSession.id);
      }
    } catch (err) {
      if (err instanceof Error) {
        setFormError(err.message);
      }
    }
  };

  const fetchSessionDetail = async (id: number) => {
    try {
      const detail = await apiGet(`/api/v1/learning/sessions/${id}`);
      setActiveSession(detail);
    } catch (err) {
      if (err instanceof Error) {
        setFormError(err.message);
      }
    }
  };

  const handleCreateSession = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    if (!title.trim()) {
      setFormError("Give your session a name.");
      return;
    }
    if (selectedMaterials.length === 0) {
      setFormError("Select at least one material.");
      return;
    }
    try {
      setLoading(true);
      const payload = {
        title,
        objective: objective || null,
        material_ids: selectedMaterials,
      };
      const session = await apiPost("/api/v1/learning/sessions", payload);
      setActiveSession(session);
      setTitle("");
      setObjective("");
      setSelectedMaterials([]);
      await refreshSessions();
    } catch (err) {
      if (err instanceof Error) {
        setFormError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (authError) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="w-full max-w-md p-8 rounded-2xl border border-neutral-200 shadow-sm text-center space-y-4">
          <p className="text-sm text-neutral-600">{authError}</p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg border border-neutral-900 bg-neutral-900 text-white"
          >
            Go to login
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="max-w-6xl mx-auto py-10 px-4 space-y-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-neutral-500">Learning workspace</p>
            <h1 className="text-2xl font-semibold">Multi-material sessions</h1>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleRefreshData}
              className="text-sm px-4 py-2 border border-neutral-200 rounded-lg hover:border-neutral-400"
            >
              Refresh data
            </button>
            <button
              type="button"
              onClick={handleLogout}
              className="text-sm px-4 py-2 border border-neutral-900 rounded-lg bg-neutral-900 text-white"
            >
              Logout
            </button>
          </div>
        </header>

        <section className="grid md:grid-cols-2 gap-6">
          <form
            onSubmit={handleCreateSession}
            className="border border-neutral-200 rounded-2xl p-6 bg-white space-y-4"
          >
            <div>
              <h2 className="text-lg font-semibold">Create a learning session</h2>
              <p className="text-sm text-neutral-500">
                Pick multiple materials and automatically build a prerequisite tree.
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="title">
                Session title
              </label>
              <input
                id="title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                className="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="objective">
                Objective <span className="text-neutral-400">(optional)</span>
              </label>
              <textarea
                id="objective"
                value={objective}
                onChange={(event) => setObjective(event.target.value)}
                rows={3}
                className="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Attach materials</p>
              <div className="max-h-48 overflow-y-auto space-y-2">
                {materials.length === 0 && (
                  <p className="text-sm text-neutral-500">
                    Upload materials first to build a session.
                  </p>
                )}
                {materials.map((material) => (
                  <label
                    key={material.id}
                    className="flex items-center gap-3 text-sm border border-neutral-200 rounded-xl px-3 py-2"
                  >
                    <input
                      type="checkbox"
                      checked={selectedMaterials.includes(material.id)}
                      onChange={() => toggleMaterial(material.id)}
                    />
                    <span className="flex-1">
                      {material.filename}
                      <span className="block text-xs text-neutral-500">
                        Status: {material.status}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {formError && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                {formError}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg border border-neutral-900 bg-neutral-900 text-white text-sm font-medium hover:bg-neutral-800 disabled:opacity-70"
            >
              {loading ? "Creating session..." : "Create session"}
            </button>
          </form>

          <div className="border border-neutral-200 rounded-2xl p-6 bg-white space-y-4">
            <div>
              <h2 className="text-lg font-semibold">Previous sessions</h2>
              <p className="text-sm text-neutral-500">
                Pick a session to view its prerequisite tree.
              </p>
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {sessions.length === 0 && (
                <p className="text-sm text-neutral-500">No sessions yet.</p>
              )}
              {sessions.map((session) => (
                <button
                  key={session.id}
                  type="button"
                  onClick={() => fetchSessionDetail(session.id)}
                  className={`w-full text-left border rounded-xl px-4 py-3 text-sm transition ${
                    activeSession?.id === session.id
                      ? "border-neutral-900 bg-neutral-900 text-white"
                      : "border-neutral-200 hover:border-neutral-400"
                  }`}
                >
                  <p className="font-medium">{session.title}</p>
                  <p className="text-xs mt-1">
                    {session.material_count} materials • {session.prerequisite_count} nodes
                  </p>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="border border-neutral-200 rounded-2xl p-6 bg-white space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Prerequisite tree</h2>
              <p className="text-sm text-neutral-500">
                Powered by the configured LLM provider + Wikipedia summaries.
              </p>
            </div>
            {activeSession && (
              <p className="text-sm text-neutral-500">
                {activeSession.materials.length} materials linked
              </p>
            )}
          </div>

          {!activeSession && (
            <p className="text-sm text-neutral-500">
              Create or select a session to view its prerequisite map.
            </p>
          )}

          {activeSession && tree.length === 0 && (
            <p className="text-sm text-neutral-500">
              No prerequisites were generated yet.
            </p>
          )}

          {activeSession && tree.length > 0 && (
            <div className="space-y-3">{renderTree(tree)}</div>
          )}
        </section>
      </div>
    </main>
  );
}
