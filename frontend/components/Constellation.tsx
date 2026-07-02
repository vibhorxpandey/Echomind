"use client";

import { useEffect, useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

const YEAR_COLORS: Record<number, THREE.Color> = {
  2021: new THREE.Color("#6d28d9"),
  2022: new THREE.Color("#7c3aed"),
  2023: new THREE.Color("#22d3ee"),
  2024: new THREE.Color("#0ea5e9"),
  2025: new THREE.Color("#8b5cf6"),
};
const YEAR_Z: Record<number, number> = {
  2021: -4, 2022: -2, 2023: 0, 2024: 2, 2025: 4,
};

const DOC_COUNT = 220; // low-poly: ~220 points total across 5 years

// Deterministic seeded random so positions don't jump on re-render
function seededRand(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function buildGeometry(flashing: Set<number>) {
  const rand = seededRand(42);
  const positions: number[] = [];
  const colors: number[] = [];
  const sizes: number[] = [];

  const years = [2021, 2022, 2023, 2024, 2025];
  const perYear = Math.floor(DOC_COUNT / years.length);

  years.forEach((year) => {
    const baseColor = YEAR_COLORS[year];
    const z = YEAR_Z[year];
    for (let i = 0; i < perYear; i++) {
      const angle = rand() * Math.PI * 2;
      const radius = 1.5 + rand() * 5.5;
      const x = Math.cos(angle) * radius * (0.7 + rand() * 0.6);
      const y = (rand() - 0.5) * 4;
      positions.push(x, y, z + (rand() - 0.5) * 2);
      const c = baseColor.clone().multiplyScalar(0.5 + rand() * 0.5);
      colors.push(c.r, c.g, c.b);
      sizes.push(1.5 + rand() * 2.5);
    }
  });

  return { positions, colors, sizes };
}

interface ParticlesProps {
  thinking: boolean;
  mouse: React.RefObject<{ x: number; y: number }>;
  chatActive: boolean;
}

function Particles({ thinking, mouse, chatActive }: ParticlesProps) {
  const pointsRef = useRef<THREE.Points>(null!);
  const groupRef = useRef<THREE.Group>(null!);
  const { gl } = useThree();

  const { positions, colors, sizes } = useMemo(() => buildGeometry(new Set()), []);

  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    g.setAttribute("size", new THREE.Float32BufferAttribute(sizes, 1));
    return g;
  }, [positions, colors, sizes]);

  const mat = useMemo(
    () =>
      new THREE.PointsMaterial({
        size: 0.06,
        vertexColors: true,
        transparent: true,
        opacity: 1,
        sizeAttenuation: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    []
  );

  // Pause render when tab is hidden
  useEffect(() => {
    const onVis = () => {
      gl.setAnimationLoop(document.hidden ? null : () => {});
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [gl]);

  let t = 0;
  useFrame((state, delta) => {
    if (!groupRef.current) return;
    t += delta;
    const baseSpeed = thinking ? 0.12 : 0.018;
    groupRef.current.rotation.y += baseSpeed * delta;

    // Damped mouse parallax — only on hero
    if (!chatActive) {
      groupRef.current.rotation.x +=
        ((mouse.current?.y ?? 0) * 0.08 - groupRef.current.rotation.x) * 0.05;
    }

    // Thinking: pulse opacity of points
    if (thinking && pointsRef.current) {
      const mat = pointsRef.current.material as THREE.PointsMaterial;
      mat.opacity = 0.7 + Math.sin(t * 4) * 0.3;
    } else if (pointsRef.current) {
      const mat = pointsRef.current.material as THREE.PointsMaterial;
      mat.opacity = chatActive ? 0.35 : 0.85;
    }
  });

  return (
    <group ref={groupRef}>
      <points ref={pointsRef} geometry={geo} material={mat} />
    </group>
  );
}

interface Props {
  thinking?: boolean;
  chatActive?: boolean;
  className?: string;
}

export default function Constellation({ thinking = false, chatActive = false, className = "" }: Props) {
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      mouseRef.current = {
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: -(e.clientY / window.innerHeight) * 2 + 1,
      };
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <div className={className}>
      <Canvas
        camera={{ position: [0, 0, 12], fov: 60 }}
        gl={{ antialias: false, alpha: true, powerPreference: "low-power" }}
        dpr={[1, 1.5]}
      >
        <Particles thinking={thinking} mouse={mouseRef} chatActive={chatActive} />
      </Canvas>
    </div>
  );
}
