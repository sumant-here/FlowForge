import WorkflowDetailClient from "./WorkflowDetailClient";

export function generateStaticParams() {
  return [
    { id: "demo-wf-diamond" },
    { id: "demo-wf-etl" }
  ];
}

export default function WorkflowDetailPage({ params }: { params: { id: string } }) {
  return <WorkflowDetailClient workflowId={params.id} />;
}