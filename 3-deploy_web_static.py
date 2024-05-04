from datetime import datetime
from fabric.api import env, local, put, run

env.hosts = ["100.26.142.212", "54.144.138.7"]


def do_pack():
  """Create a tar gzipped archive of the directory web_static."""
  dt = datetime.utcnow()
  file = f"versions/web_static_{dt.year}{dt.month}{dt.day}{dt.hour}{dt.minute}{dt.second}.tgz"
  try:
    if not os.path.isdir("versions"):
      local("mkdir -p versions")  # Create versions directory if missing
    if local(f"tar -cvzf {file} web_static").failed:
      return None
  except Exception as e:
    print(f"Packing error: {e}")
    return None
  return file


def do_deploy(archive_path):
  """Distributes an archive to a web server.

  Args:
      archive_path (str): The path of the archive to distribute.
  Returns:
      True if successful, False otherwise.
  """
  if not os.path.isfile(archive_path):
    return False
  file = archive_path.split("/")[-1]
  name = file.split(".")[0]

  try:
    if put(archive_path, f"/tmp/{file}").failed:
      return False
    if run(f"rm -rf /data/web_static/releases/{name}/").failed:
      return False
    if run(f"mkdir -p /data/web_static/releases/{name}/").failed:
      return False
    if run(f"tar -xzf /tmp/{file} -C /data/web_static/releases/{name}/").failed:
      return False
    if run(f"rm /tmp/{file}").failed:
      return False
    if run(f"mv /data/web_static/releases/{name}/web_static/* /data/web_static/releases/{name}/").failed:
      return False
    if run(f"rm -rf /data/web_static/releases/{name}/web_static").failed:
      return False
    if run(f"rm -rf /data/web_static/current").failed:
      return False
    if run(f"ln -s /data/web_static/releases/{name} /data/web_static/current").failed:
      return False
  except Exception as e:
    print(f"Deployment error: {e}")
    return False
  return True


def deploy():
  """Create and distribute an archive to a web server."""
  file = do_pack()
  if not file:
    return False
  return do_deploy(file)
