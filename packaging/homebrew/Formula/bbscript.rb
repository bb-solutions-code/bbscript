# Homebrew third-party tap (copy to a repo named homebrew-bbscript or add tap path).
# After publishing GitHub release assets, replace url/sha256 and version for each platform.

class Bbscript < Formula
  desc "BBScript graph runtime (bbscript) and package manager (bbpm) with bundled Foblox"
  homepage "https://github.com/bb-solutions-code/bbscript"
  version "0.2.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/bb-solutions-code/bbscript/releases/download/v0.2.0/bbscript-0.2.0-darwin-arm64.tar.gz"
      sha256 "REPLACE_WITH_SHA256"
    else
      url "https://github.com/bb-solutions-code/bbscript/releases/download/v0.2.0/bbscript-0.2.0-darwin-x64.tar.gz"
      sha256 "REPLACE_WITH_SHA256"
    end
  end

  on_linux do
    url "https://github.com/bb-solutions-code/bbscript/releases/download/v0.2.0/bbscript-0.2.0-linux-x86_64.tar.gz"
    sha256 "REPLACE_WITH_SHA256"
  end

  def install
    libexec.install Dir["bbscript-bundle/*"]
    bin.install_symlink libexec/"bbscript" => "bbscript"
    bin.install_symlink libexec/"bbpm" => "bbpm"
  end

  test do
    system bin/"bbscript", "--help"
    system bin/"bbpm", "--help"
  end
end
