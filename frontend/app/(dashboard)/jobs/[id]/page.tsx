import JobDetailClient from "./JobDetailClient";

export function generateStaticParams() {
  return [
    { id: "demo-prime-1000" },
    { id: "demo-etl-transform" },
    { id: "demo-pdf-report" }
  ];
}

export default function JobDetailPage({ params }: { params: { id: string } }) {
  return <JobDetailClient jobId={params.id} />;
}