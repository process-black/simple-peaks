"use client";
import React, { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { marked } from "marked";

export default function ArtistPage() {
  const params = useParams();
  const artist = Array.isArray(params.artist) ? params.artist[0] : params.artist;

  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const videoRef = useRef<HTMLVideoElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [fps, setFps] = useState(30);
  const [frame, setFrame] = useState(0);
  const [last, setLast] = useState(0);

  const isDesktop = () => window.innerWidth >= 768;

  useEffect(() => {
    const video = videoRef.current!;
    const scroller = scrollRef.current!;

    const onMeta = async () => {
      if (
        video.duration &&
        typeof (video as any).webkitDecodedFrameCount === "number"
      ) {
        setFps(
          Math.round((video as any).webkitDecodedFrameCount / video.duration) ||
            30
        );
      }
      try {
        await video.play();
        video.pause();
      } catch {}
      video.currentTime = 0;
    };
    video.addEventListener("loadedmetadata", onMeta, { once: true });

    const stopLoop = () => video.pause();
    video.addEventListener("play", stopLoop);

    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const scrollPos = isDesktop() ? scroller.scrollTop : window.scrollY;
        const maxScroll = isDesktop()
          ? scroller.scrollHeight - scroller.clientHeight
          : document.body.scrollHeight - window.innerHeight;
        const progress = Math.min(scrollPos / maxScroll, 1);
        const target = progress * video.duration;

        if (Math.abs(target - last) > 1 / fps) {
          video.currentTime = target;
          video.pause();
          setLast(target);
          setFrame(Math.floor(target * fps));
        }
        ticking = false;
      });
    };

    const scrollTarget: any = isDesktop() ? scroller : window;
    scrollTarget.addEventListener("scroll", onScroll, { passive: true });

    return () => {
      scrollTarget.removeEventListener("scroll", onScroll);
      video.removeEventListener("play", stopLoop);
    };
  }, [fps, last]);

  const [markdown, setMarkdown] = useState("");
  useEffect(() => {
    fetch(`/artists/${artist}/bio.md`)
      .then((res) => res.text())
      .then((text) => setMarkdown(text));
  }, [artist]);

  // Convert markdown to array of paragraphs
  const paragraphs = markdown
    .split(/\n\s*\n/)
    .map((para) => para.trim())
    .filter(Boolean);

  return (
    <main className="relative flex flex-col md:flex-row w-full overflow-x-hidden">
      {/* 🎞 video */}
      <video
        ref={videoRef}
        src={`/artists/${artist}/video.mp4`}
        muted
        playsInline
        preload="auto"
        className="
          fixed inset-0 -z-10 h-screen w-screen object-cover
          md:static md:w-1/2 md:h-screen
        "
      />

      {/* 📑 text */}
      <div
        ref={scrollRef}
        className="relative z-10 w-full flex flex-col items-center md:w-1/2 md:h-screen md:overflow-y-auto"
      >
        {paragraphs.map((para, i) => (
          <section key={i} className="flex flex-col items-center justify-center w-full px-4">
            <article
              className={
                `${isMobile ? 'bg-black/50 backdrop-blur-none' : 'bg-black/70 backdrop-blur-sm'} text-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto break-words w-full`
              }
            >
              <div
                className="text-lg leading-relaxed drop-shadow-lg m-0"
                dangerouslySetInnerHTML={{ __html: marked.parseInline(para) }}
              />
            </article>
            {i < paragraphs.length - 1 && (
              <div style={{ height: '100vh', width: '100%' }} />
            )}
          </section>
        ))}
      </div>

      {/* 🔢 frame readout */}
      <div className="fixed bottom-4 right-4 rounded bg-black/70 px-3 py-2 font-mono text-sm text-white">
        Frame&nbsp;{frame}
      </div>
    </main>
  );
}
