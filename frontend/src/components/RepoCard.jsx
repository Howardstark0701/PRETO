import { Star, GitFork, Eye, ExternalLink } from 'lucide-react'

export default function RepoCard({ repo }) {
  return (
    <div className="repo-card">
      <div className="repo-card-name">
        <a href={repo.html_url} target="_blank" rel="noreferrer">
          {repo.full_name || repo.name}
        </a>
      </div>
      <div className="repo-card-desc">
        {repo.description || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No description</span>}
      </div>
      <div className="repo-card-meta">
        <span><Star size={11} /> {(repo.stargazers_count || 0).toLocaleString()}</span>
        <span><GitFork size={11} /> {(repo.forks_count || 0).toLocaleString()}</span>
        <span><Eye size={11} /> {(repo.watchers_count || 0).toLocaleString()}</span>
        {repo.language && <span className="tag">{repo.language}</span>}
      </div>
    </div>
  )
}
