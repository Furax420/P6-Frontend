import { execFileSync, spawnSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';

const digestFormat = /^sha256:[a-f0-9]{64}$/;

function imageReferences({ env, nextRelease }) {
  const repository = env.RELEASE_IMAGE_REPOSITORY;
  const digest = env.RELEASE_IMAGE_DIGEST;
  if (!/^ghcr\.io\/[a-z0-9-]+\/[a-z0-9._-]+$/.test(repository) || !digestFormat.test(digest)) {
    throw new Error('The build job must provide a GHCR image repository and digest.');
  }

  return {
    source: `${repository}@${digest}`,
    target: `${repository}:${nextRelease.version}`,
    digest,
  };
}

function inspectDigest(ref, allowMissing = false) {
  const result = spawnSync('docker', [
    'buildx', 'imagetools', 'inspect', '--format', '{{.Manifest.Digest}}', ref,
  ], { encoding: 'utf8' });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    const message = result.stderr.trim();
    if (allowMissing && /:\s*not found\s*$|manifest unknown/i.test(message)) return null;
    throw new Error(`Could not inspect ${ref}: ${message}`);
  }

  const digest = result.stdout.trim();
  if (!digestFormat.test(digest)) throw new Error(`Invalid image digest for ${ref}.`);
  return digest;
}

export function verifyRelease(_options, context) {
  imageReferences(context);
  if (context.nextRelease.gitHead !== context.env.GITHUB_SHA) {
    throw new Error('The release commit must match the commit built by the workflow.');
  }
}

export function generateNotes(_options, context) {
  const { target, digest } = imageReferences(context);
  return [
    '### Docker image',
    '',
    `- Image \`${target}\``,
    `- Source commit \`${context.env.GITHUB_SHA}\``,
    `- Digest \`${digest}\``,
  ].join('\n');
}

export function prepare(_options, context) {
  const { source, target, digest } = imageReferences(context);
  const existing = inspectDigest(target, true);
  if (existing !== null && existing !== digest) {
    throw new Error(`The released tag ${target} already points to ${existing}.`);
  }

  if (existing === null) {
    execFileSync('docker', [
      'buildx', 'imagetools', 'create', '--prefer-index=false', '--tag', target, source,
    ], { stdio: 'inherit' });
    if (inspectDigest(target) !== digest) {
      throw new Error(`The released tag ${target} does not match the build image digest.`);
    }
  }

  context.logger.log('GHCR image %s points to %s', target, digest);
  if (context.env.GITHUB_STEP_SUMMARY) {
    appendFileSync(context.env.GITHUB_STEP_SUMMARY,
      `\n### Docker release image\n\n\`${target}\`\n\nDigest \`${digest}\`\n`);
  }
}
